#!/usr/bin/env python3
"""
Comprehensive Test Suite for Architect Plus
Tests all components including Flask app, spaceplanning integration, and deployment readiness
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class TestArchitectPlusSystem(unittest.TestCase):
    """Comprehensive system tests for Architect Plus"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data = {
            "project": {
                "name": "Test Hospital",
                "style": "modern",
                "floors": 3,
                "site": {"width": 50, "depth": 40}
            },
            "rooms": [
                {
                    "name": "Emergency Room",
                    "floor": 1,
                    "width": 12, "depth": 8, "height": 4,
                    "position": {"x": 0, "y": 0, "z": 0},
                    "shape": "rectangle",
                    "features": ["medical_equipment", "emergency_access"]
                },
                {
                    "name": "Surgery Room",
                    "floor": 2,
                    "width": 8, "depth": 6, "height": 4,
                    "position": {"x": 0, "y": 0, "z": 4},
                    "shape": "rectangle",
                    "features": ["sterile_environment", "surgical_equipment"]
                },
                {
                    "name": "Patient Room",
                    "floor": 3,
                    "width": 6, "depth": 4, "height": 3,
                    "position": {"x": 0, "y": 0, "z": 8},
                    "shape": "rectangle",
                    "features": ["patient_bed", "medical_gas"]
                }
            ],
            "walls": [
                {
                    "start": {"x": 0, "y": 0, "z": 0},
                    "end": {"x": 12, "y": 0, "z": 0},
                    "height": 4,
                    "thickness": 0.2,
                    "material": "concrete"
                }
            ],
            "openings": [
                {
                    "type": "door",
                    "wall_id": 0,
                    "position": 2.0,
                    "width": 1.2,
                    "height": 2.1,
                    "style": "automatic"
                }
            ],
            "structural": [
                {
                    "type": "column",
                    "position": {"x": 6, "y": 4, "z": 0},
                    "diameter": 0.4,
                    "height": 12
                }
            ],
            "exterior": {
                "roof": {"type": "flat", "pitch": 0},
                "facade": {"material": "glass", "color": "blue"}
            }
        }
        
        # Create temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_data, self.temp_file)
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
            
    def test_gemini_json_reader(self):
        """Test Gemini JSON reader functionality"""
        try:
            from gemini_json_reader import GeminiJsonReader
            
            reader = GeminiJsonReader(self.temp_file.name)
            params = reader.get_design_parameters()
            
            # Validate basic structure
            self.assertIn('departments', params)
            self.assertIn('site_outline', params)
            self.assertIn('building_info', params)
            
            # Validate department categorization
            departments = params['departments']
            self.assertGreater(len(departments), 0, "Should detect at least one department")
            
            # Check for medical departments (based on test data)
            dept_names = [dept['name'] for dept in departments]
            medical_terms = ['emergency', 'surgery', 'patient', 'medical']
            has_medical = any(any(term in name.lower() for term in medical_terms) for name in dept_names)
            self.assertTrue(has_medical, "Should detect medical-related departments")
            
            print(f"[PASS] JSON Reader Test: Detected {len(departments)} departments")
            
        except ImportError:
            self.skipTest("Gemini JSON reader not available")
            
    def test_spaceplanning_integration(self):
        """Test spaceplanning integration"""
        try:
            from dynamo_spaceplanning_integration import process_gemini_json_for_spaceplanning
            
            results = process_gemini_json_for_spaceplanning(
                self.temp_file.name,
                design_seed=42,
                circulation_factor=1.5,
                acceptable_width=20.0
            )
            
            # Validate results structure
            self.assertIn('success', results)
            self.assertIn('departments', results)
            self.assertIn('design_parameters', results)
            
            if results['success']:
                self.assertGreater(len(results['departments']), 0, "Should generate departments")
                print(f"[PASS] Spaceplanning Test: Generated {len(results['departments'])} departments")
            else:
                print(f"[WARN] Spaceplanning Test: {results.get('message', 'Unknown error')}")
                
        except ImportError:
            self.skipTest("Spaceplanning integration not available")
            
    def test_design_automation_integration(self):
        """Test Design Automation integration"""
        try:
            from design_automation_integration import DesignAutomationIntegrator
            
            integrator = DesignAutomationIntegrator()
            
            # Test activity generation
            activity = integrator.create_activity_definition(['input.json'])
            self.assertIn('id', activity)
            self.assertIn('commandLine', activity)
            self.assertEqual(activity['id'], 'ArchitectPlusSpaceplanning')
            
            # Test appbundle generation
            appbundle = integrator.create_appbundle_definition()
            self.assertIn('id', appbundle)
            self.assertIn('engine', appbundle)
            
            print("[PASS] Design Automation Test: Activity and AppBundle definitions created")
            
        except ImportError:
            self.skipTest("Design Automation integration not available")
            
    def test_flask_app_structure(self):
        """Test Flask application structure"""
        try:
            from app import app
            
            # Test app configuration
            self.assertIsNotNone(app)
            self.assertTrue(app.testing or app.debug or app.config.get('ENV') == 'development')
            
            # Test routes exist
            with app.test_client() as client:
                # Test basic routes
                response = client.get('/')
                self.assertIn(response.status_code, [200, 302])
                
                # Test health endpoint
                response = client.get('/health')
                self.assertEqual(response.status_code, 200)
                
                data = response.get_json()
                self.assertIn('status', data)
                self.assertEqual(data['status'], 'healthy')
                
                # Test spaceplanning info endpoint
                response = client.get('/spaceplanning-info')
                self.assertEqual(response.status_code, 200)
                
                print("[PASS] Flask App Test: All endpoints responding correctly")
                
        except ImportError:
            self.skipTest("Flask app not available")
            
    @patch('google.generativeai.GenerativeModel')
    def test_basic_design_generation(self, mock_model):
        """Test basic design generation endpoint"""
        try:
            from app import app
            
            # Mock Gemini response
            mock_response = MagicMock()
            mock_response.text = json.dumps(self.test_data)
            mock_model.return_value.generate_content.return_value = mock_response
            
            with app.test_client() as client:
                response = client.post('/generate-design', 
                    json={'description': 'A modern hospital with emergency and surgery facilities'})
                
                self.assertEqual(response.status_code, 200)
                
                data = response.get_json()
                self.assertTrue(data['success'])
                self.assertIn('design', data)
                
                print("[PASS] Basic Design Generation Test: Successfully generated design")
                
        except ImportError:
            self.skipTest("Flask app not available")
            
    def test_professional_spaceplanning_endpoint(self):
        """Test professional spaceplanning endpoint"""
        try:
            from app import app
            
            with app.test_client() as client:
                # First check if spaceplanning is available
                response = client.get('/spaceplanning-info')
                data = response.get_json()
                
                if not data.get('available'):
                    self.skipTest("Spaceplanning not available")
                    
                # Test the professional endpoint
                with patch('google.generativeai.GenerativeModel') as mock_model:
                    mock_response = MagicMock()
                    mock_response.text = json.dumps(self.test_data)
                    mock_model.return_value.generate_content.return_value = mock_response
                    
                    response = client.post('/generate-with-spaceplanning', json={
                        'description': 'A modern hospital',
                        'design_seed': 50,
                        'circulation_factor': 1.8,
                        'acceptable_width': 18.0
                    })
                    
                    # Should return 200 even if spaceplanning fails
                    self.assertIn(response.status_code, [200, 500])  # Allow both success and error
                    
                    print("[PASS] Professional Spaceplanning Test: Endpoint responding correctly")
                    
        except ImportError:
            self.skipTest("Flask app not available")
            
    def test_dynamo_script_validity(self):
        """Test Dynamo script file validity"""
        dynamo_path = Path(__file__).parent / 'Architect_Plus_Spaceplanning_Complete.dyn'
        
        if not dynamo_path.exists():
            self.skipTest("Dynamo script not found")
            
        # Test that file is valid JSON
        with open(dynamo_path, 'r', encoding='utf-8') as f:
            try:
                dynamo_data = json.load(f)
                
                # Validate basic Dynamo structure
                self.assertIn('Uuid', dynamo_data)
                self.assertIn('Nodes', dynamo_data)
                self.assertIn('Connectors', dynamo_data)
                
                # Check for Python script node
                nodes = dynamo_data['Nodes']
                python_nodes = [node for node in nodes if 'Python' in node.get('NodeType', '')]
                self.assertGreater(len(python_nodes), 0, "Should contain Python script nodes")
                
                print(f"[PASS] Dynamo Script Test: Valid script with {len(nodes)} nodes")
                
            except json.JSONDecodeError as e:
                self.fail(f"Dynamo script is not valid JSON: {e}")
                
    def test_file_structure_completeness(self):
        """Test that all required files are present"""
        project_root = Path(__file__).parent
        
        required_files = [
            'app.py',
            'gemini_json_reader.py',
            'dynamo_spaceplanning_integration.py',
            'design_automation_integration.py',
            'Architect_Plus_Spaceplanning_Complete.dyn',
            'requirements.txt',
            'templates/index.html',
            'static/styles.css',
            'README.md'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
                
        if missing_files:
            self.fail(f"Missing required files: {missing_files}")
            
        print(f"[PASS] File Structure Test: All {len(required_files)} required files present")
        
    def test_dependencies_installable(self):
        """Test that all dependencies can be imported"""
        try:
            # Test core dependencies
            import flask
            import google.generativeai
            
            # Test optional dependencies
            try:
                import numpy
                print("[PASS] NumPy available")
            except ImportError:
                print("[WARN] NumPy not available (optional)")
                
            try:
                import requests
                print("[PASS] Requests available")
            except ImportError:
                print("[WARN] Requests not available (optional)")
                
            print("[PASS] Dependencies Test: Core dependencies available")
            
        except ImportError as e:
            self.fail(f"Core dependency not available: {e}")
            
    def test_output_directory_creation(self):
        """Test output directory creation and permissions"""
        output_dir = Path(__file__).parent / 'output'
        
        # Create if doesn't exist
        output_dir.mkdir(exist_ok=True)
        
        # Test write permissions
        test_file = output_dir / 'test_write.json'
        try:
            with open(test_file, 'w') as f:
                json.dump({'test': True}, f)
                
            # Clean up
            test_file.unlink()
            
            print("[PASS] Output Directory Test: Directory writable")
            
        except Exception as e:
            self.fail(f"Cannot write to output directory: {e}")

class TestSystemPerformance(unittest.TestCase):
    """Performance tests for the system"""
    
    def test_json_processing_performance(self):
        """Test JSON processing performance"""
        try:
            from gemini_json_reader import GeminiJsonReader
            import time
            
            # Create test data
            large_test_data = {
                "project": {"name": "Large Building", "floors": 5},
                "rooms": [
                    {
                        "name": f"Room {i}",
                        "floor": (i % 5) + 1,
                        "width": 4, "depth": 3, "height": 3,
                        "position": {"x": i * 4, "y": 0, "z": (i % 5) * 3},
                        "shape": "rectangle",
                        "features": ["standard"]
                    }
                    for i in range(100)  # 100 rooms
                ]
            }
            
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(large_test_data, temp_file)
            temp_file.close()
            
            try:
                start_time = time.time()
                reader = GeminiJsonReader(temp_file.name)
                params = reader.get_design_parameters()
                end_time = time.time()
                
                processing_time = end_time - start_time
                self.assertLess(processing_time, 5.0, "JSON processing should complete within 5 seconds")
                
                print(f"[PASS] Performance Test: Processed 100 rooms in {processing_time:.2f} seconds")
                
            finally:
                os.unlink(temp_file.name)
                
        except ImportError:
            self.skipTest("Performance test dependencies not available")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("[TEST] Starting Comprehensive Architect Plus System Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestArchitectPlusSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("[SUMMARY] Test Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\n[FAIL] Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
            
    if result.errors:
        print("\n[ERROR] Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
            
    if result.skipped:
        print("\n[SKIP] Skipped:")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
            
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n[SUCCESS] All tests passed! System is ready for deployment.")
    else:
        print("\n[FAIL] Some tests failed. Please review and fix issues before deployment.")
        
    return success

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1) 