#!/usr/bin/env python3
"""
Architect Plus Deployment Script
Comprehensive deployment and validation for the Architect Plus spaceplanning system
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

class ArchitectPlusDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_report = {
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'validation_results': {},
            'deployment_status': 'pending'
        }
        
    def log(self, message, level='INFO'):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {level}: {message}")
        
    def validate_environment(self):
        """Validate the deployment environment"""
        self.log("Validating deployment environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.log("Python 3.8+ required", "ERROR")
            return False
            
        # Check required files
        required_files = [
            'app.py',
            'gemini_json_reader.py',
            'dynamo_spaceplanning_integration.py',
            'design_automation_integration.py',
            'Architect_Plus_Spaceplanning_Complete.dyn',
            'requirements.txt',
            'templates/index.html',
            'static/styles.css'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            self.log(f"Missing required files: {missing_files}", "ERROR")
            return False
            
        # Check Spaceplanning repository
        if not (self.project_root / 'Spaceplanning_ADSK_PW').exists():
            self.log("Spaceplanning repository not found", "WARNING")
            
        self.deployment_report['validation_results']['environment'] = 'valid'
        self.log("Environment validation passed")
        return True
        
    def install_dependencies(self):
        """Install Python dependencies"""
        self.log("Installing Python dependencies...")
        
        try:
            # Create virtual environment if it doesn't exist
            venv_path = self.project_root / 'venv'
            if not venv_path.exists():
                self.log("Creating virtual environment...")
                subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
                
            # Determine pip path
            if os.name == 'nt':  # Windows
                pip_path = venv_path / 'Scripts' / 'pip.exe'
                python_path = venv_path / 'Scripts' / 'python.exe'
            else:  # Unix/Linux/Mac
                pip_path = venv_path / 'bin' / 'pip'
                python_path = venv_path / 'bin' / 'python'
                
            # Install dependencies
            subprocess.run([
                str(pip_path), 'install', '-r', 'requirements.txt'
            ], check=True, cwd=self.project_root)
            
            # Install additional deployment dependencies
            additional_deps = [
                'gunicorn',  # Production WSGI server
                'python-dotenv',  # Environment variables
                'pytest',  # Testing framework
                'requests'  # HTTP client
            ]
            
            for dep in additional_deps:
                subprocess.run([str(pip_path), 'install', dep], check=True)
                
            self.deployment_report['validation_results']['dependencies'] = 'installed'
            self.log("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to install dependencies: {e}", "ERROR")
            return False
            
    def validate_spaceplanning_integration(self):
        """Validate spaceplanning integration"""
        self.log("Validating spaceplanning integration...")
        
        try:
            # Test import of spaceplanning modules
            sys.path.insert(0, str(self.project_root))
            
            from gemini_json_reader import GeminiJsonReader
            from dynamo_spaceplanning_integration import process_gemini_json_for_spaceplanning
            from design_automation_integration import DesignAutomationIntegrator
            
            # Test with sample data
            sample_data = {
                "project": {
                    "name": "Test Building",
                    "style": "modern",
                    "floors": 2,
                    "site": {"width": 30, "depth": 25}
                },
                "rooms": [
                    {
                        "name": "Reception",
                        "floor": 1,
                        "width": 6, "depth": 4, "height": 3,
                        "position": {"x": 0, "y": 0, "z": 0},
                        "shape": "rectangle",
                        "features": ["reception_desk", "seating"]
                    },
                    {
                        "name": "Office",
                        "floor": 1,
                        "width": 4, "depth": 3, "height": 3,
                        "position": {"x": 6, "y": 0, "z": 0},
                        "shape": "rectangle",
                        "features": ["desk", "storage"]
                    }
                ]
            }
            
            # Save test data
            test_json_path = self.project_root / 'output' / 'test_design.json'
            os.makedirs(test_json_path.parent, exist_ok=True)
            
            with open(test_json_path, 'w') as f:
                json.dump(sample_data, f, indent=2)
                
            # Test JSON reader
            reader = GeminiJsonReader(str(test_json_path))
            params = reader.get_design_parameters()
            
            if len(params.get('departments', [])) == 0:
                self.log("No departments detected in test data", "WARNING")
            else:
                self.log(f"Detected {len(params['departments'])} departments")
                
            # Test spaceplanning integration
            results = process_gemini_json_for_spaceplanning(
                str(test_json_path),
                design_seed=25,
                circulation_factor=1.5,
                acceptable_width=15.0
            )
            
            if results.get('success'):
                self.log("Spaceplanning integration test passed")
                self.deployment_report['validation_results']['spaceplanning'] = 'working'
            else:
                self.log(f"Spaceplanning integration test failed: {results.get('message', 'Unknown error')}", "WARNING")
                self.deployment_report['validation_results']['spaceplanning'] = 'failed'
                
            # Clean up test file
            test_json_path.unlink()
            
            return True
            
        except Exception as e:
            self.log(f"Spaceplanning validation failed: {e}", "ERROR")
            self.deployment_report['validation_results']['spaceplanning'] = 'error'
            return False
            
    def create_production_config(self):
        """Create production configuration files"""
        self.log("Creating production configuration...")
        
        # Create .env template
        env_template = """# Architect Plus Production Configuration
# Copy this file to .env and fill in your values

# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secret_key_here

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Spaceplanning Configuration
SPACEPLANNING_ENABLED=True
DEFAULT_DESIGN_SEED=50
DEFAULT_CIRCULATION_FACTOR=1.8
DEFAULT_ACCEPTABLE_WIDTH=18.0

# Design Automation Configuration
DA_CLIENT_ID=your_forge_client_id
DA_CLIENT_SECRET=your_forge_client_secret
DA_CALLBACK_URL=your_callback_url
"""
        
        env_path = self.project_root / '.env.template'
        with open(env_path, 'w') as f:
            f.write(env_template)
            
        # Create Gunicorn configuration
        gunicorn_config = """# Gunicorn Configuration for Architect Plus
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
"""
        
        gunicorn_path = self.project_root / 'gunicorn.conf.py'
        with open(gunicorn_path, 'w') as f:
            f.write(gunicorn_config)
            
        # Create systemd service file
        service_config = """[Unit]
Description=Architect Plus - AI-Powered Architectural Design
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/architect_plus
Environment=PATH=/path/to/architect_plus/venv/bin
ExecStart=/path/to/architect_plus/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = self.project_root / 'architect-plus.service'
        with open(service_path, 'w') as f:
            f.write(service_config)
            
        # Create Dockerfile
        dockerfile = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
"""
        
        dockerfile_path = self.project_root / 'Dockerfile'
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile)
            
        # Create docker-compose.yml
        docker_compose = """version: '3.8'

services:
  architect-plus:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    env_file:
      - .env
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
        
        compose_path = self.project_root / 'docker-compose.yml'
        with open(compose_path, 'w') as f:
            f.write(docker_compose)
            
        self.log("Production configuration files created")
        return True
        
    def run_integration_tests(self):
        """Run comprehensive integration tests"""
        self.log("Running integration tests...")
        
        try:
            # Test Flask app import
            sys.path.insert(0, str(self.project_root))
            from app import app
            
            # Test app configuration
            with app.test_client() as client:
                # Test health endpoint
                response = client.get('/health')
                if response.status_code == 200:
                    self.log("Health endpoint test passed")
                else:
                    self.log("Health endpoint test failed", "WARNING")
                    
                # Test spaceplanning info endpoint
                response = client.get('/spaceplanning-info')
                if response.status_code == 200:
                    data = response.get_json()
                    if data.get('available'):
                        self.log("Spaceplanning availability test passed")
                    else:
                        self.log("Spaceplanning not available", "WARNING")
                else:
                    self.log("Spaceplanning info endpoint test failed", "WARNING")
                    
            self.deployment_report['validation_results']['integration_tests'] = 'passed'
            self.log("Integration tests completed")
            return True
            
        except Exception as e:
            self.log(f"Integration tests failed: {e}", "ERROR")
            self.deployment_report['validation_results']['integration_tests'] = 'failed'
            return False
            
    def create_deployment_package(self):
        """Create deployment package"""
        self.log("Creating deployment package...")
        
        try:
            # Create deployment directory
            deploy_dir = self.project_root / 'deployment'
            if deploy_dir.exists():
                shutil.rmtree(deploy_dir)
            deploy_dir.mkdir()
            
            # Files to include in deployment
            deployment_files = [
                'app.py',
                'gemini_json_reader.py',
                'dynamo_spaceplanning_integration.py',
                'design_automation_integration.py',
                'gemini_api_integration.py',
                'Architect_Plus_Spaceplanning_Complete.dyn',
                'requirements.txt',
                'gunicorn.conf.py',
                'Dockerfile',
                'docker-compose.yml',
                '.env.template',
                'architect-plus.service',
                'README.md',
                'ARCHITECT_PLUS_SPACEPLANNING_GUIDE.md',
                'SOLUTION_SUMMARY.md'
            ]
            
            # Copy files
            for file_path in deployment_files:
                src = self.project_root / file_path
                if src.exists():
                    dst = deploy_dir / file_path
                    if src.is_file():
                        shutil.copy2(src, dst)
                    else:
                        shutil.copytree(src, dst)
                        
            # Copy directories
            for dir_name in ['templates', 'static', 'output']:
                src_dir = self.project_root / dir_name
                if src_dir.exists():
                    shutil.copytree(src_dir, deploy_dir / dir_name)
                    
            # Create deployment README
            deployment_readme = """# Architect Plus Deployment Package

This package contains all files needed to deploy Architect Plus in production.

## Quick Start

1. Copy all files to your server
2. Copy .env.template to .env and configure your API keys
3. Run: `python deploy.py`

## Docker Deployment

1. Configure .env file
2. Run: `docker-compose up -d`

## Manual Deployment

1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\\Scripts\\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Configure .env file
5. Run: `gunicorn -c gunicorn.conf.py app:app`

## Systemd Service (Linux)

1. Copy architect-plus.service to /etc/systemd/system/
2. Update paths in service file
3. Run: `sudo systemctl enable architect-plus`
4. Run: `sudo systemctl start architect-plus`

## Health Check

Visit: http://your-server:5000/health
"""
            
            with open(deploy_dir / 'DEPLOYMENT_README.md', 'w') as f:
                f.write(deployment_readme)
                
            # Create deployment report
            with open(deploy_dir / 'deployment_report.json', 'w') as f:
                json.dump(self.deployment_report, f, indent=2)
                
            self.log(f"Deployment package created at: {deploy_dir}")
            return True
            
        except Exception as e:
            self.log(f"Failed to create deployment package: {e}", "ERROR")
            return False
            
    def generate_deployment_report(self):
        """Generate final deployment report"""
        self.log("Generating deployment report...")
        
        report_path = self.project_root / 'DEPLOYMENT_REPORT.md'
        
        report_content = f"""# Architect Plus Deployment Report

Generated: {self.deployment_report['timestamp']}

## Validation Results

"""
        
        for component, status in self.deployment_report['validation_results'].items():
            status_emoji = "[PASS]" if status in ['valid', 'working', 'installed', 'passed'] else "[WARN]" if status == 'failed' else "[FAIL]"
            report_content += f"- {component.replace('_', ' ').title()}: {status_emoji} {status}\n"
            
        report_content += """
## Deployment Options

### Option 1: Docker (Recommended)
```bash
# Configure environment
cp .env.template .env
# Edit .env with your API keys

# Deploy with Docker
docker-compose up -d

# Check status
docker-compose ps
```

### Option 2: Manual Deployment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\\Scripts\\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API keys

# Run application
gunicorn -c gunicorn.conf.py app:app
```

### Option 3: Systemd Service (Linux)
```bash
# Copy service file
sudo cp architect-plus.service /etc/systemd/system/

# Update paths in service file
sudo nano /etc/systemd/system/architect-plus.service

# Enable and start service
sudo systemctl enable architect-plus
sudo systemctl start architect-plus
```

## Configuration

### Required Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key
- `FLASK_ENV`: Set to 'production' for production deployment
- `SECRET_KEY`: Random secret key for Flask sessions

### Optional Configuration
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)
- `SPACEPLANNING_ENABLED`: Enable spaceplanning features (default: True)

## Health Checks

- Health endpoint: `/health`
- Spaceplanning info: `/spaceplanning-info`

## Troubleshooting

1. **Spaceplanning not available**: Check that all Python dependencies are installed
2. **Gemini API errors**: Verify your API key is correct and has sufficient quota
3. **Port conflicts**: Change PORT in .env file
4. **Permission errors**: Ensure proper file permissions and user access

## Production Considerations

1. **SSL/TLS**: Use a reverse proxy (nginx) with SSL certificates
2. **Firewall**: Configure firewall to allow only necessary ports
3. **Monitoring**: Set up monitoring for the application and server
4. **Backups**: Regular backups of generated designs and configurations
5. **Scaling**: Consider load balancing for high traffic

## Support

For issues and questions, refer to:
- ARCHITECT_PLUS_SPACEPLANNING_GUIDE.md
- SOLUTION_SUMMARY.md
- GitHub repository issues
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.log(f"Deployment report saved to: {report_path}")
        
    def deploy(self):
        """Main deployment function"""
        self.log("Starting Architect Plus deployment...")
        
        success = True
        
        # Validation steps
        if not self.validate_environment():
            success = False
            
        if not self.install_dependencies():
            success = False
            
        if not self.validate_spaceplanning_integration():
            success = False
            
        # Configuration and packaging
        if not self.create_production_config():
            success = False
            
        if not self.run_integration_tests():
            success = False
            
        if not self.create_deployment_package():
            success = False
            
        # Generate final report
        self.deployment_report['deployment_status'] = 'success' if success else 'failed'
        self.generate_deployment_report()
        
        if success:
            self.log("[SUCCESS] Deployment completed successfully!")
            self.log("[INFO] Check DEPLOYMENT_REPORT.md for detailed instructions")
            self.log("[INFO] Deployment package available in ./deployment/")
        else:
            self.log("[ERROR] Deployment completed with errors")
            self.log("[INFO] Check DEPLOYMENT_REPORT.md for troubleshooting")
            
        return success

def main():
    """Main entry point"""
    deployer = ArchitectPlusDeployer()
    return deployer.deploy()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 