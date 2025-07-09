"""
Design Automation Integration for Architect Plus Spaceplanning
Handles execution of Dynamo graphs in Revit Design Automation environment
"""

import os
import json
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

class DesignAutomationIntegrator:
    """Handles Design Automation workflow for Architect Plus Spaceplanning"""
    
    def __init__(self, work_dir: str = None):
        """Initialize with working directory"""
        self.work_dir = work_dir or os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        self.results = {}
        
    def prepare_input_files(self, gemini_json_path: str, design_params: Dict[str, Any] = None) -> Dict[str, str]:
        """Prepare input files for Design Automation"""
        input_files = {}
        
        # Copy Gemini JSON to temp directory
        temp_json_path = os.path.join(self.temp_dir, "design_input.json")
        
        if os.path.exists(gemini_json_path):
            import shutil
            shutil.copy2(gemini_json_path, temp_json_path)
        else:
            # Create default JSON if not found
            self.create_default_json(temp_json_path)
        
        input_files['design_json'] = temp_json_path
        
        # Create design parameters file
        if design_params:
            params_path = os.path.join(self.temp_dir, "design_params.json")
            with open(params_path, 'w') as f:
                json.dump(design_params, f, indent=2)
            input_files['design_params'] = params_path
        
        # Copy Dynamo graph
        dynamo_graph_path = os.path.join(self.temp_dir, "spaceplanning_graph.dyn")
        self.copy_dynamo_graph(dynamo_graph_path)
        input_files['dynamo_graph'] = dynamo_graph_path
        
        # Copy Python modules
        self.copy_python_modules()
        input_files['python_modules'] = self.temp_dir
        
        return input_files
    
    def create_default_json(self, output_path: str):
        """Create default JSON for testing"""
        default_json = {
            "project": {
                "name": "Default Medical Center",
                "style": "Modern",
                "floors": 3,
                "site": {
                    "width": 100,
                    "depth": 150
                }
            },
            "rooms": [
                {
                    "name": "Emergency Department",
                    "floor": 1,
                    "width": 20,
                    "depth": 15,
                    "height": 3.5,
                    "position": {"x": 10, "y": 10, "z": 0},
                    "shape": "rectangle",
                    "features": ["Triage area", "Trauma bays"]
                },
                {
                    "name": "Surgical Suite",
                    "floor": 2,
                    "width": 15,
                    "depth": 15,
                    "height": 3.0,
                    "position": {"x": 10, "y": 40, "z": 3.5},
                    "shape": "rectangle",
                    "features": ["Operating table", "Anesthesia machine"]
                },
                {
                    "name": "Patient Room",
                    "floor": 3,
                    "width": 6,
                    "depth": 5,
                    "height": 3.0,
                    "position": {"x": 10, "y": 70, "z": 7},
                    "shape": "rectangle",
                    "features": ["Bed", "Bathroom"]
                }
            ],
            "walls": [
                {
                    "start": {"x": 0, "y": 0, "z": 0},
                    "end": {"x": 100, "y": 0, "z": 0},
                    "height": 3.5,
                    "thickness": 0.2,
                    "material": "Concrete"
                }
            ],
            "structural": [
                {
                    "type": "column",
                    "position": {"x": 20, "y": 20, "z": 0},
                    "diameter": 0.5,
                    "height": 10.5,
                    "cross_section": "circular"
                }
            ],
            "exterior": {
                "roof": {"type": "flat", "pitch": 0},
                "facade": {"material": "Glass and Metal", "color": "Silver"}
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(default_json, f, indent=2)
    
    def copy_dynamo_graph(self, output_path: str):
        """Copy Dynamo graph to temp directory"""
        source_path = "Architect_Plus_Spaceplanning_Complete.dyn"
        
        if os.path.exists(source_path):
            import shutil
            shutil.copy2(source_path, output_path)
        else:
            # Create minimal graph structure
            minimal_graph = {
                "Uuid": "3c9d0464-8643-5ffe-96e5-ab1769818209",
                "IsCustomNode": False,
                "Description": "Architect Plus Spaceplanning for Design Automation",
                "Name": "Architect_Plus_Spaceplanning_DA",
                "Nodes": [],
                "Connectors": [],
                "Dependencies": [],
                "View": {
                    "Dynamo": {
                        "Version": "2.19.0.5742",
                        "RunType": "Manual"
                    }
                }
            }
            
            with open(output_path, 'w') as f:
                json.dump(minimal_graph, f, indent=2)
    
    def copy_python_modules(self):
        """Copy Python modules to temp directory"""
        modules_to_copy = [
            'gemini_json_reader.py',
            'dynamo_spaceplanning_integration.py'
        ]
        
        for module in modules_to_copy:
            if os.path.exists(module):
                import shutil
                dest_path = os.path.join(self.temp_dir, module)
                shutil.copy2(module, dest_path)
    
    def create_activity_definition(self, input_files: Dict[str, str]) -> Dict[str, Any]:
        """Create Design Automation activity definition"""
        activity = {
            "id": "ArchitectPlusSpaceplanning",
            "commandLine": [
                "$(engine.path)\\\\revit.exe",
                "/i", "$(args[designJson].path)",
                "/al", "$(appbundles[ArchitectPlusBundle].path)"
            ],
            "parameters": {
                "designJson": {
                    "verb": "get",
                    "description": "Input Gemini JSON file",
                    "required": True,
                    "localName": "design_input.json"
                },
                "designParams": {
                    "verb": "get",
                    "description": "Design parameters",
                    "required": False,
                    "localName": "design_params.json"
                },
                "result": {
                    "verb": "put",
                    "description": "Output Revit model",
                    "required": True,
                    "localName": "result.rvt"
                },
                "geometryJson": {
                    "verb": "put",
                    "description": "Generated geometry data",
                    "required": False,
                    "localName": "geometry_output.json"
                }
            },
            "engine": "Autodesk.Revit+2026",
            "appbundles": ["ArchitectPlusBundle"],
            "description": "Generate architectural geometry from text using Gemini AI and Spaceplanning"
        }
        
        return activity
    
    def create_appbundle_definition(self) -> Dict[str, Any]:
        """Create Design Automation appbundle definition"""
        appbundle = {
            "id": "ArchitectPlusBundle",
            "engine": "Autodesk.Revit+2026",
            "description": "Architect Plus Spaceplanning Bundle",
            "package": "ArchitectPlusPackage.zip"
        }
        
        return appbundle
    
    def create_package_structure(self, input_files: Dict[str, str]) -> str:
        """Create package structure for Design Automation"""
        package_dir = os.path.join(self.temp_dir, "package")
        os.makedirs(package_dir, exist_ok=True)
        
        # Create Contents.xml
        contents_xml = '''<?xml version="1.0" encoding="utf-8"?>
<ApplicationPackage 
    SchemaVersion="1.0" 
    AutodeskProduct="Revit" 
    ProductType="Application" 
    Name="ArchitectPlusSpaceplanning" 
    AppVersion="1.0" 
    Author="Architect Plus" 
    Description="AI-powered architectural design generation">
    
    <CompanyDetails 
        Name="Architect Plus" 
        Url="https://architectplus.ai" 
        Email="support@architectplus.ai" />
    
    <RuntimeRequirements 
        OS="Win64" 
        Platform="Any CPU" 
        SeriesMin="R2026" 
        SeriesMax="R2026" />
    
    <ComponentEntry 
        AppName="ArchitectPlusSpaceplanning" 
        Version="1.0" 
        ModuleName="./ArchitectPlusSpaceplanning.dll" 
        AppDescription="Generate architectural geometry from text prompts" 
        LoadOnCommandInvocation="True" 
        LoadOnRevitStartup="True" />
        
</ApplicationPackage>'''
        
        with open(os.path.join(package_dir, "Contents.xml"), 'w') as f:
            f.write(contents_xml)
        
        # Copy files to package
        import shutil
        
        # Copy Dynamo graph
        shutil.copy2(input_files['dynamo_graph'], 
                    os.path.join(package_dir, "spaceplanning_graph.dyn"))
        
        # Copy Python modules
        for file in os.listdir(input_files['python_modules']):
            if file.endswith('.py'):
                shutil.copy2(os.path.join(input_files['python_modules'], file),
                           os.path.join(package_dir, file))
        
        # Create main assembly (placeholder)
        self.create_main_assembly(package_dir)
        
        # Create package zip
        package_zip = os.path.join(self.temp_dir, "ArchitectPlusPackage.zip")
        shutil.make_archive(package_zip[:-4], 'zip', package_dir)
        
        return package_zip
    
    def create_main_assembly(self, package_dir: str):
        """Create main assembly for Design Automation"""
        # Create a placeholder C# file that would be compiled to DLL
        csharp_code = '''
using System;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Autodesk.Revit.Attributes;
using DesignAutomationFramework;

namespace ArchitectPlusSpaceplanning
{
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class SpaceplanningCommand : IExternalDBApplication
    {
        public ExternalDBApplicationResult OnStartup(ControlledApplication application)
        {
            DesignAutomationBridge.DesignAutomationReadyEvent += HandleDesignAutomationReady;
            return ExternalDBApplicationResult.Succeeded;
        }

        public ExternalDBApplicationResult OnShutdown(ControlledApplication application)
        {
            return ExternalDBApplicationResult.Succeeded;
        }

        private void HandleDesignAutomationReady(object sender, DesignAutomationReadyEventArgs e)
        {
            e.Succeeded = ProcessSpaceplanning(e.DesignAutomationData);
        }

        private bool ProcessSpaceplanning(DesignAutomationData data)
        {
            try
            {
                // Execute Dynamo graph with spaceplanning logic
                // This would integrate with the Python modules and Dynamo graph
                
                Application app = data.RevitApp;
                Document doc = data.RevitDoc;
                
                // Process the Gemini JSON and generate geometry
                // Implementation would call the Dynamo graph execution
                
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in spaceplanning: {ex.Message}");
                return false;
            }
        }
    }
}
'''
        
        # Save C# code (in real implementation, this would be compiled to DLL)
        with open(os.path.join(package_dir, "SpaceplanningCommand.cs"), 'w') as f:
            f.write(csharp_code)
        
        # Create placeholder DLL (in real implementation, compile the C# code)
        dll_path = os.path.join(package_dir, "ArchitectPlusSpaceplanning.dll")
        with open(dll_path, 'wb') as f:
            f.write(b'Placeholder DLL content')
    
    def create_workitem_definition(self, input_files: Dict[str, str]) -> Dict[str, Any]:
        """Create Design Automation workitem definition"""
        workitem = {
            "activityId": "ArchitectPlusSpaceplanning",
            "arguments": {
                "designJson": {
                    "verb": "get",
                    "url": input_files['design_json']
                },
                "result": {
                    "verb": "put",
                    "url": "https://your-storage-url/result.rvt"
                },
                "geometryJson": {
                    "verb": "put",
                    "url": "https://your-storage-url/geometry_output.json"
                }
            }
        }
        
        if 'design_params' in input_files:
            workitem["arguments"]["designParams"] = {
                "verb": "get",
                "url": input_files['design_params']
            }
        
        return workitem
    
    def execute_local_test(self, input_files: Dict[str, str]) -> Dict[str, Any]:
        """Execute local test of the spaceplanning logic"""
        try:
            # Import and run the spaceplanning integration
            sys.path.append(self.temp_dir)
            from dynamo_spaceplanning_integration import process_gemini_json_for_spaceplanning
            
            # Run spaceplanning
            results = process_gemini_json_for_spaceplanning(
                json_path=input_files['design_json'],
                design_seed=50,
                circulation_factor=1.8,
                acceptable_width=18.0
            )
            
            # Save results
            output_path = os.path.join(self.temp_dir, "local_test_results.json")
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            return {
                'success': True,
                'results': results,
                'output_file': output_path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_design_automation_files(self, gemini_json_path: str, 
                                       design_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate all Design Automation files"""
        try:
            # Prepare input files
            input_files = self.prepare_input_files(gemini_json_path, design_params)
            
            # Create activity definition
            activity = self.create_activity_definition(input_files)
            
            # Create appbundle definition
            appbundle = self.create_appbundle_definition()
            
            # Create package
            package_zip = self.create_package_structure(input_files)
            
            # Create workitem definition
            workitem = self.create_workitem_definition(input_files)
            
            # Run local test
            test_results = self.execute_local_test(input_files)
            
            # Save all definitions
            definitions_dir = os.path.join(self.temp_dir, "definitions")
            os.makedirs(definitions_dir, exist_ok=True)
            
            with open(os.path.join(definitions_dir, "activity.json"), 'w') as f:
                json.dump(activity, f, indent=2)
            
            with open(os.path.join(definitions_dir, "appbundle.json"), 'w') as f:
                json.dump(appbundle, f, indent=2)
            
            with open(os.path.join(definitions_dir, "workitem.json"), 'w') as f:
                json.dump(workitem, f, indent=2)
            
            return {
                'success': True,
                'temp_dir': self.temp_dir,
                'input_files': input_files,
                'package_zip': package_zip,
                'activity': activity,
                'appbundle': appbundle,
                'workitem': workitem,
                'test_results': test_results,
                'definitions_dir': definitions_dir
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

# Main execution for testing
if __name__ == "__main__":
    integrator = DesignAutomationIntegrator()
    
    # Test with default parameters
    design_params = {
        'design_seed': 50,
        'circulation_factor': 1.8,
        'acceptable_width': 18.0,
        'kpu_depth': 15.0,
        'kpu_width': 10.0
    }
    
    results = integrator.generate_design_automation_files(
        "output/design.json", 
        design_params
    )
    
    if results['success']:
        print("Design Automation files generated successfully!")
        print(f"Temp directory: {results['temp_dir']}")
        print(f"Package: {results['package_zip']}")
        print(f"Test results: {results['test_results']['success']}")
    else:
        print(f"Error: {results['error']}")
    
    # Don't cleanup for inspection
    # integrator.cleanup() 