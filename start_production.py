#!/usr/bin/env python3
"""
Production startup script for Architect Plus
Handles environment setup, dependency checking, and server startup
"""

import os
import sys
import json
import time
import signal
import logging
import argparse
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ProductionManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.pid_file = self.project_root / 'architect_plus.pid'
        self.log_file = self.project_root / 'architect_plus.log'
        self.is_windows = platform.system() == 'Windows'
        
    def log(self, message, level='INFO'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        getattr(logging, level.lower())(message)
        
    def check_environment(self):
        """Check environment configuration"""
        self.log("Checking environment configuration...")
        
        # Check for .env file
        env_file = self.project_root / '.env'
        if not env_file.exists():
            self.log("No .env file found. Creating template...", 'WARNING')
            self.create_env_template()
            
        # Load environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            
            # Check required variables
            required_vars = ['GEMINI_API_KEY']
            missing_vars = []
            
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
                    
            if missing_vars:
                self.log(f"Missing required environment variables: {missing_vars}", 'ERROR')
                self.log("Please configure your .env file with the required variables", 'ERROR')
                return False
                
            self.log("Environment configuration valid")
            return True
            
        except ImportError:
            self.log("python-dotenv not installed. Installing...", 'WARNING')
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-dotenv'], check=True)
            return self.check_environment()
            
    def create_env_template(self):
        """Create .env template file"""
        env_template = """# Architect Plus Environment Configuration
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
HOST=0.0.0.0
PORT=5000
SPACEPLANNING_ENABLED=True
"""
        with open(self.project_root / '.env', 'w') as f:
            f.write(env_template)
            
    def check_dependencies(self):
        """Check and install dependencies"""
        self.log("Checking dependencies...")
        
        # Check core dependencies
        try:
            import flask
            import google.generativeai
            self.log("Core dependencies available")
        except ImportError as e:
            self.log(f"Missing core dependency: {e}", 'ERROR')
            self.log("Installing dependencies...", 'INFO')
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            
        # Check spaceplanning integration
        try:
            from gemini_json_reader import GeminiJsonReader
            from dynamo_spaceplanning_integration import process_gemini_json_for_spaceplanning
            self.log("Spaceplanning integration available")
        except ImportError:
            self.log("Spaceplanning integration not available", 'WARNING')
            
        # Install production server
        if self.is_windows:
            try:
                import waitress
                self.log("Waitress WSGI server available")
            except ImportError:
                self.log("Waitress not found. Installing...", 'WARNING')
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'waitress'], check=True)
        else:
            try:
                import gunicorn
                self.log("Gunicorn WSGI server available")
            except ImportError:
                self.log("Gunicorn not found. Installing...", 'WARNING')
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn'], check=True)
                
        self.log("Dependencies check passed")
        return True
        
    def create_directories(self):
        """Create necessary directories"""
        self.log("Creating necessary directories...")
        
        directories = [
            self.project_root / 'output',
            self.project_root / 'logs',
            self.project_root / 'temp'
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            
        self.log("Directories created")
        
    def start_development(self):
        """Start development server"""
        self.log("Starting in development mode...")
        
        try:
            # Import and run Flask app directly
            sys.path.insert(0, str(self.project_root))
            from app import app
            
            host = os.getenv('HOST', '127.0.0.1')
            port = int(os.getenv('PORT', 5000))
            
            self.log(f"Starting Flask development server on {host}:{port}")
            app.run(host=host, port=port, debug=True)
            
        except Exception as e:
            self.log(f"Failed to start development server: {e}", 'ERROR')
            return False
            
    def start_production(self):
        """Start production server"""
        self.log("Starting in production mode...")
        
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        
        try:
            if self.is_windows:
                # Use Waitress on Windows
                self.log("Starting Waitress server...")
                cmd = [
                    sys.executable, '-m', 'waitress',
                    '--host', host,
                    '--port', str(port),
                    '--threads', '4',
                    '--connection-limit', '1000',
                    '--cleanup-interval', '30',
                    '--channel-timeout', '120',
                    'app:app'
                ]
            else:
                # Use Gunicorn on Unix-like systems
                self.log("Starting Gunicorn server...")
                cmd = [
                    'gunicorn',
                    '--bind', f'{host}:{port}',
                    '--workers', '4',
                    '--timeout', '30',
                    '--keep-alive', '2',
                    '--max-requests', '1000',
                    '--max-requests-jitter', '50',
                    '--preload',
                    '--pid', str(self.pid_file),
                    'app:app'
                ]
            
            # Start the server
            self.log(f"Command: {' '.join(cmd)}")
            process = subprocess.Popen(cmd, cwd=self.project_root)
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
                
            self.log(f"Server started with PID {process.pid}")
            self.log(f"Application available at http://{host}:{port}")
            self.log("Press Ctrl+C to stop the server")
            
            # Wait for process
            try:
                process.wait()
            except KeyboardInterrupt:
                self.log("Stopping server...")
                process.terminate()
                process.wait()
                
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to start production server: {e}", 'ERROR')
            return False
        except Exception as e:
            self.log(f"Unexpected error: {e}", 'ERROR')
            return False
            
        return True
        
    def stop_server(self):
        """Stop running server"""
        if not self.pid_file.exists():
            self.log("No PID file found. Server may not be running.", 'WARNING')
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            if self.is_windows:
                # Windows process termination
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True)
            else:
                # Unix process termination
                os.kill(pid, signal.SIGTERM)
                
            self.pid_file.unlink()
            self.log(f"Server stopped (PID: {pid})")
            return True
            
        except (FileNotFoundError, ProcessLookupError):
            self.log("Server process not found", 'WARNING')
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
        except Exception as e:
            self.log(f"Error stopping server: {e}", 'ERROR')
            return False
            
    def restart_server(self):
        """Restart server"""
        self.log("Restarting server...")
        self.stop_server()
        time.sleep(2)
        return self.start_production()
        
    def get_status(self):
        """Get server status"""
        if not self.pid_file.exists():
            self.log("Server is not running")
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            if self.is_windows:
                # Check if process exists on Windows
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True)
                if str(pid) in result.stdout:
                    self.log(f"Server is running (PID: {pid})")
                    return True
                else:
                    self.log("Server PID file exists but process is not running")
                    self.pid_file.unlink()
                    return False
            else:
                # Check if process exists on Unix
                os.kill(pid, 0)  # This will raise an exception if process doesn't exist
                self.log(f"Server is running (PID: {pid})")
                return True
                
        except (FileNotFoundError, ProcessLookupError, OSError):
            self.log("Server is not running")
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
        except Exception as e:
            self.log(f"Error checking status: {e}", 'ERROR')
            return False
            
    def health_check(self):
        """Perform health check"""
        try:
            import requests
            
            host = os.getenv('HOST', '127.0.0.1')
            port = int(os.getenv('PORT', 5000))
            
            response = requests.get(f'http://{host}:{port}/health', timeout=10)
            
            if response.status_code == 200:
                self.log("Health check passed")
                return True
            else:
                self.log(f"Health check failed: HTTP {response.status_code}", 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"Health check failed: {e}", 'ERROR')
            return False

def main():
    parser = argparse.ArgumentParser(description='Architect Plus Production Manager')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'health'], 
                       help='Action to perform')
    parser.add_argument('--mode', choices=['development', 'production'], default='production',
                       help='Server mode')
    
    args = parser.parse_args()
    
    manager = ProductionManager()
    
    if args.action == 'start':
        # Pre-flight checks
        if not manager.check_environment():
            sys.exit(1)
            
        if not manager.check_dependencies():
            sys.exit(1)
            
        manager.create_directories()
        
        # Start server
        if args.mode == 'development':
            success = manager.start_development()
        else:
            success = manager.start_production()
            
        sys.exit(0 if success else 1)
        
    elif args.action == 'stop':
        success = manager.stop_server()
        sys.exit(0 if success else 1)
        
    elif args.action == 'restart':
        success = manager.restart_server()
        sys.exit(0 if success else 1)
        
    elif args.action == 'status':
        success = manager.get_status()
        sys.exit(0 if success else 1)
        
    elif args.action == 'health':
        success = manager.health_check()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 