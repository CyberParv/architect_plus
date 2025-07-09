#!/usr/bin/env python3
"""
Architect Plus Project Status Checker
Final validation and status report for the complete project
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

def check_file_exists(file_path, description):
    """Check if a file exists and return status"""
    if Path(file_path).exists():
        size = Path(file_path).stat().st_size
        print(f"[OK] {description}: {file_path} ({size:,} bytes)")
        return True
    else:
        print(f"[MISSING] {description}: {file_path}")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and return status"""
    if Path(dir_path).exists() and Path(dir_path).is_dir():
        files = list(Path(dir_path).iterdir())
        print(f"[OK] {description}: {dir_path} ({len(files)} items)")
        return True
    else:
        print(f"[MISSING] {description}: {dir_path}")
        return False

def main():
    """Main status check function"""
    print("=" * 60)
    print("ARCHITECT PLUS PROJECT STATUS CHECK")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Core Application Files
    print("CORE APPLICATION FILES:")
    core_files = [
        ("app.py", "Flask Web Application"),
        ("gemini_json_reader.py", "Gemini JSON Reader"),
        ("dynamo_spaceplanning_integration.py", "Spaceplanning Integration"),
        ("design_automation_integration.py", "Design Automation"),
        ("gemini_api_integration.py", "Gemini API Integration"),
        ("requirements.txt", "Python Dependencies"),
    ]
    
    core_status = []
    for file_path, description in core_files:
        core_status.append(check_file_exists(file_path, description))
    
    print()
    
    # Dynamo Files
    print("DYNAMO INTEGRATION:")
    dynamo_files = [
        ("Architect_Plus_Spaceplanning_Complete.dyn", "Complete Dynamo Script"),
    ]
    
    dynamo_status = []
    for file_path, description in dynamo_files:
        dynamo_status.append(check_file_exists(file_path, description))
    
    print()
    
    # Web Interface Files
    print("WEB INTERFACE:")
    web_files = [
        ("templates/index.html", "Main HTML Template"),
        ("static/styles.css", "CSS Styles"),
    ]
    
    web_status = []
    for file_path, description in web_files:
        web_status.append(check_file_exists(file_path, description))
    
    print()
    
    # Documentation
    print("DOCUMENTATION:")
    doc_files = [
        ("README.md", "Project README"),
        ("ARCHITECT_PLUS_SPACEPLANNING_GUIDE.md", "User Guide"),
        ("SOLUTION_SUMMARY.md", "Solution Summary"),
    ]
    
    doc_status = []
    for file_path, description in doc_files:
        doc_status.append(check_file_exists(file_path, description))
    
    print()
    
    # Testing and Deployment
    print("TESTING & DEPLOYMENT:")
    test_files = [
        ("complete_integration_test.py", "Integration Tests"),
        ("test_complete_system.py", "System Tests"),
        ("deploy.py", "Deployment Script"),
        ("start_production.py", "Production Launcher"),
    ]
    
    test_status = []
    for file_path, description in test_files:
        test_status.append(check_file_exists(file_path, description))
    
    print()
    
    # Directories
    print("DIRECTORIES:")
    directories = [
        ("output", "Output Directory"),
        ("Spaceplanning_ADSK_PW", "Spaceplanning Repository"),
        ("templates", "HTML Templates"),
        ("static", "Static Assets"),
    ]
    
    dir_status = []
    for dir_path, description in directories:
        dir_status.append(check_directory_exists(dir_path, description))
    
    print()
    
    # Check if sample data exists
    print("SAMPLE DATA:")
    sample_files = [
        ("sample_rooms.json", "Sample Room Data"),
        ("output/design.json", "Generated Design (if exists)"),
    ]
    
    sample_status = []
    for file_path, description in sample_files:
        exists = check_file_exists(file_path, description)
        sample_status.append(exists)
    
    print()
    
    # Test imports
    print("PYTHON IMPORTS:")
    import_tests = [
        ("flask", "Flask Framework"),
        ("google.generativeai", "Google Gemini AI"),
    ]
    
    import_status = []
    for module_name, description in import_tests:
        try:
            __import__(module_name)
            print(f"[OK] {description}: {module_name}")
            import_status.append(True)
        except ImportError:
            print(f"[MISSING] {description}: {module_name} (NOT AVAILABLE)")
            import_status.append(False)
    
    # Test spaceplanning integration
    try:
        from gemini_json_reader import GeminiJsonReader
        from dynamo_spaceplanning_integration import process_gemini_json_for_spaceplanning
        print("[OK] Spaceplanning Integration: Available")
        spaceplanning_available = True
    except ImportError:
        print("[MISSING] Spaceplanning Integration: Not Available")
        spaceplanning_available = False
    
    print()
    
    # Summary
    print("=" * 60)
    print("PROJECT STATUS SUMMARY")
    print("=" * 60)
    
    total_core = len(core_files)
    passed_core = sum(core_status)
    print(f"Core Application Files: {passed_core}/{total_core} ({'PASS' if passed_core == total_core else 'FAIL'})")
    
    total_dynamo = len(dynamo_files)
    passed_dynamo = sum(dynamo_status)
    print(f"Dynamo Integration: {passed_dynamo}/{total_dynamo} ({'PASS' if passed_dynamo == total_dynamo else 'FAIL'})")
    
    total_web = len(web_files)
    passed_web = sum(web_status)
    print(f"Web Interface: {passed_web}/{total_web} ({'PASS' if passed_web == total_web else 'FAIL'})")
    
    total_doc = len(doc_files)
    passed_doc = sum(doc_status)
    print(f"Documentation: {passed_doc}/{total_doc} ({'PASS' if passed_doc == total_doc else 'FAIL'})")
    
    total_test = len(test_files)
    passed_test = sum(test_status)
    print(f"Testing & Deployment: {passed_test}/{total_test} ({'PASS' if passed_test == total_test else 'FAIL'})")
    
    total_dir = len(directories)
    passed_dir = sum(dir_status)
    print(f"Directory Structure: {passed_dir}/{total_dir} ({'PASS' if passed_dir == total_dir else 'FAIL'})")
    
    total_import = len(import_tests)
    passed_import = sum(import_status)
    print(f"Python Dependencies: {passed_import}/{total_import} ({'PASS' if passed_import == total_import else 'FAIL'})")
    
    print(f"Spaceplanning Integration: {'AVAILABLE' if spaceplanning_available else 'NOT AVAILABLE'}")
    
    print()
    
    # Overall status
    all_critical = (
        passed_core == total_core and
        passed_dynamo == total_dynamo and
        passed_web == total_web and
        passed_import == total_import and
        spaceplanning_available
    )
    
    if all_critical:
        print("[SUCCESS] PROJECT STATUS: READY FOR PRODUCTION")
        print()
        print("NEXT STEPS:")
        print("1. Configure .env file with your Gemini API key")
        print("2. Run: python start_production.py start --mode production")
        print("3. Access the application at http://localhost:5000")
        print("4. Test both Basic Design and Professional Spaceplanning modes")
        print()
        return True
    else:
        print("[WARNING] PROJECT STATUS: NEEDS ATTENTION")
        print()
        print("Please review the missing components above before deployment.")
        print()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 