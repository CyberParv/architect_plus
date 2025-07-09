#!/usr/bin/env python3
"""
Setup script for Architect Plus
This script helps you set up the application quickly
"""

import os
import sys

def create_env_file():
    """Create a .env file with user input"""
    print("🏗️ Architect Plus Setup")
    print("=" * 50)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("⚠️  .env file already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Get API key from user
    print("\n📋 Please provide your Google Gemini API key:")
    print("   Get it from: https://makersuite.google.com/app/apikey")
    
    api_key = input("🔑 Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ API key is required!")
        sys.exit(1)
    
    # Create .env file
    env_content = f"""# Google Gemini API Configuration
GEMINI_API_KEY={api_key}

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("[SUCCESS] .env file created successfully!")

def install_dependencies():
    """Install Python dependencies"""
    print("\n[INFO] Installing dependencies...")
    os.system("pip install -r requirements.txt")
    print("[SUCCESS] Dependencies installed!")

def main():
    """Main setup function"""
    print("Welcome to Architect Plus setup!")
    print("This script will help you configure the application.\n")
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    install_choice = input("\n🔧 Install dependencies now? (Y/n): ").lower()
    if install_choice != 'n':
        install_dependencies()
    
    print("\n🎉 Setup complete!")
    print("\nTo run the application:")
    print("   python app.py")
    print("\nThen open: http://localhost:5000")

if __name__ == "__main__":
    main() 