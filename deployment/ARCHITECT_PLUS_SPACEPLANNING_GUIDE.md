# Architect Plus Spaceplanning Complete Solution

## Overview

This is a complete architectural design automation solution that integrates:
- **Gemini AI** for text-to-architectural-design generation
- **Spaceplanning Zero-Touch Nodes** for intelligent space layout
- **Dynamo** for parametric design workflows
- **Revit Design Automation** for cloud-based execution
- **CPython3** for modern Python integration

## Architecture

```
Text Prompt → Gemini AI → JSON Design → Spaceplanning Logic → 3D Geometry → Revit Model
```

## Key Components

### 1. Gemini JSON Reader (`gemini_json_reader.py`)
- Processes Gemini-generated architectural JSON
- Converts to Spaceplanning-compatible data structures
- Handles department categorization and adjacency analysis
- Supports multiple building types (hospital, office, residential, etc.)

### 2. Dynamo Spaceplanning Integration (`dynamo_spaceplanning_integration.py`)
- Integrates with Spaceplanning zero-touch nodes
- Provides CPython3 compatibility
- Handles geometric operations and layout generation
- Includes fallback mechanisms for missing dependencies

### 3. Complete Dynamo Graph (`Architect_Plus_Spaceplanning_Complete.dyn`)
- Self-contained Dynamo workflow
- Processes JSON input to 3D geometry output
- Compatible with Revit 2026 and Design Automation
- Includes comprehensive error handling

### 4. Design Automation Integration (`design_automation_integration.py`)
- Prepares files for Autodesk Design Automation
- Creates activity and appbundle definitions
- Handles cloud execution workflows
- Includes local testing capabilities

## Installation & Setup

### Prerequisites
- Revit 2026 (for local testing)
- Dynamo 2.19+ 
- Python 3.8+
- Autodesk Design Automation account (for cloud execution)

### Local Setup

1. **Clone and Install Dependencies**
```bash
git clone https://github.com/Dewb/Spaceplanning_ADSK_PW.git
cd architect_plus
pip install -r requirements.txt
```

2. **Copy Spaceplanning DLL**
```bash
# Copy SpacePlanning.dll to Dynamo packages folder
# Typically: %APPDATA%\Dynamo\Dynamo Revit\2.19\packages\
```

3. **Test JSON Processing**
```bash
python gemini_json_reader.py
```

4. **Test Spaceplanning Integration**
```bash
python dynamo_spaceplanning_integration.py
```

## Usage

### 1. Generate Design with Gemini AI

Use your existing Gemini API integration to generate JSON from text prompts:

```python
# Your existing Gemini integration
prompt = "Design a modern 3-story medical center with emergency department, surgical suites, and patient rooms"
design_json = generate_with_gemini(prompt)  # Your function
```

### 2. Process with Spaceplanning

#### Option A: Direct Python Processing
```python
from dynamo_spaceplanning_integration import process_gemini_json_for_spaceplanning

results = process_gemini_json_for_spaceplanning(
    json_path="output/design.json",
    design_seed=50,
    circulation_factor=1.8,
    acceptable_width=18.0
)

if results['success']:
    print(f"Generated {len(results['departments'])} departments")
    print(f"Created {len(results['geometry_3d'])} 3D elements")
```

#### Option B: Dynamo Graph Execution
1. Open `Architect_Plus_Spaceplanning_Complete.dyn` in Dynamo
2. Set JSON file path input
3. Adjust design parameters
4. Run the graph
5. View generated geometry in 3D preview

### 3. Design Automation Deployment

```python
from design_automation_integration import DesignAutomationIntegrator

integrator = DesignAutomationIntegrator()

# Generate all Design Automation files
results = integrator.generate_design_automation_files(
    "output/design.json",
    design_params={
        'design_seed': 50,
        'circulation_factor': 1.8,
        'acceptable_width': 18.0
    }
)

if results['success']:
    print(f"Package created: {results['package_zip']}")
    print(f"Activity definition: {results['activity']}")
```

## Configuration

### Design Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `design_seed` | Random seed for layout generation | 50 | 1-100 |
| `circulation_factor` | Multiplier for circulation area | 1.8 | 1.0-3.0 |
| `acceptable_width` | Minimum acceptable room width | 18.0 | 10.0-30.0 |
| `kpu_depth` | Key Planning Unit depth | 15.0 | 10.0-30.0 |
| `kpu_width` | Key Planning Unit width | 10.0 | 8.0-25.0 |
| `grid_spacing` | Grid spacing for layout | 5.0 | 2.0-10.0 |
| `floor_height` | Standard floor height | 3.5 | 2.5-5.0 |

### Building Type Configurations

#### Hospital/Medical
```python
config = {
    'circulation_factor': 1.8,  # Higher circulation for medical
    'acceptable_width': 18.0,
    'adjacency_weights': {
        'emergency': 3.0,
        'surgical': 3.0,
        'patient_care': 2.0
    }
}
```

#### Office
```python
config = {
    'circulation_factor': 1.4,  # Lower circulation for office
    'acceptable_width': 12.0,
    'adjacency_weights': {
        'executive': 2.0,
        'meeting': 2.5,
        'workstation': 1.0
    }
}
```

#### Residential
```python
config = {
    'circulation_factor': 1.3,  # Minimal circulation
    'acceptable_width': 10.0,
    'adjacency_weights': {
        'bedroom': 2.0,
        'kitchen': 2.5,
        'living': 1.5
    }
}
```

## Advanced Features

### 1. Custom Room Shapes
The system supports multiple room shapes:
- Rectangle (default)
- L-shaped
- Circular
- Custom polygons

### 2. Multi-Floor Buildings
Automatic floor-by-floor layout with:
- Vertical circulation planning
- Structural alignment
- Services coordination

### 3. Adjacency Analysis
Intelligent room placement based on:
- Functional relationships
- Traffic patterns
- Privacy requirements
- Accessibility standards

### 4. Structural Integration
Automatic placement of:
- Columns and beams
- Load-bearing walls
- Foundations
- Mechanical systems

## Output Formats

### 1. Geometry Data
- Department polygons
- Program polygons
- Circulation networks
- 3D building geometry
- Site outline

### 2. Building Data
```json
{
    "departments": ["Emergency Department", "Surgical Department"],
    "total_area": 15000,
    "floors": 3,
    "circulation_area": 2700,
    "efficiency_ratio": 0.85
}
```

### 3. Revit Model
- Native Revit families
- Proper categorization
- Material assignments
- View templates
- Schedules and annotations

## API Reference

### GeminiJsonReader Class

```python
reader = GeminiJsonReader("design.json")

# Get design parameters
params = reader.get_design_parameters()

# Get department data
departments = reader.get_department_data()

# Get site outline
outline = reader.get_site_outline_points()

# Export to Spaceplanning format
reader.export_to_spaceplanning_format("output.csv")
```

### DynamoSpaceplanningIntegrator Class

```python
integrator = DynamoSpaceplanningIntegrator("design.json")

# Run complete workflow
results = integrator.run_complete_spaceplanning(design_seed=50)

# Place departments
departments = integrator.place_departments_on_site(design_seed=50)

# Generate 3D geometry
geometry = integrator.generate_3d_geometry(departments, height=3.5)
```

### DesignAutomationIntegrator Class

```python
integrator = DesignAutomationIntegrator()

# Generate DA files
results = integrator.generate_design_automation_files(
    "design.json", 
    design_params
)

# Run local test
test_results = integrator.execute_local_test(input_files)
```

## Troubleshooting

### Common Issues

1. **ProtoGeometry not available**
   - Solution: Uses fallback mock geometry classes
   - Check: Dynamo installation and references

2. **Spaceplanning DLL not found**
   - Solution: Copy SpacePlanning.dll to Dynamo packages
   - Check: DLL compatibility with Dynamo version

3. **JSON parsing errors**
   - Solution: Validate JSON structure against schema
   - Check: Gemini AI output format

4. **Design Automation failures**
   - Solution: Check activity and appbundle definitions
   - Check: File upload permissions and URLs

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug information
results = process_gemini_json_for_spaceplanning(
    json_path="design.json",
    design_seed=50,
    circulation_factor=1.8,
    acceptable_width=18.0
)
```

## Performance Optimization

### 1. Caching
- Cache Gemini API responses
- Store processed geometry data
- Reuse Spaceplanning calculations

### 2. Parallel Processing
- Multi-threaded department placement
- Parallel geometry generation
- Concurrent Design Automation jobs

### 3. Memory Management
- Stream large JSON files
- Dispose geometry objects properly
- Clean up temporary files

## Integration Examples

### 1. Web Application Integration

```python
from flask import Flask, request, jsonify
from dynamo_spaceplanning_integration import process_gemini_json_for_spaceplanning

app = Flask(__name__)

@app.route('/generate-design', methods=['POST'])
def generate_design():
    data = request.json
    prompt = data.get('prompt')
    
    # Generate with Gemini (your existing code)
    design_json = generate_with_gemini(prompt)
    
    # Process with Spaceplanning
    results = process_gemini_json_for_spaceplanning(
        json_path=design_json,
        design_seed=data.get('seed', 50),
        circulation_factor=data.get('circulation', 1.8)
    )
    
    return jsonify(results)
```

### 2. Desktop Application Integration

```python
import tkinter as tk
from tkinter import filedialog, messagebox
from dynamo_spaceplanning_integration import DynamoSpaceplanningIntegrator

class ArchitectPlusGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Architect Plus Spaceplanning")
        self.setup_ui()
    
    def setup_ui(self):
        # File selection
        tk.Button(self.root, text="Select JSON", 
                 command=self.select_json).pack()
        
        # Parameters
        self.seed_var = tk.IntVar(value=50)
        tk.Scale(self.root, from_=1, to=100, variable=self.seed_var,
                orient=tk.HORIZONTAL, label="Design Seed").pack()
        
        # Generate button
        tk.Button(self.root, text="Generate Design", 
                 command=self.generate_design).pack()
    
    def generate_design(self):
        integrator = DynamoSpaceplanningIntegrator(self.json_path)
        results = integrator.run_complete_spaceplanning(self.seed_var.get())
        
        if results['success']:
            messagebox.showinfo("Success", "Design generated successfully!")
        else:
            messagebox.showerror("Error", results['message'])
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project integrates with:
- Spaceplanning_ADSK_PW (original license applies)
- Autodesk Design Automation (commercial license required)
- Google Gemini AI (API usage terms apply)

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Documentation: [Wiki](https://github.com/your-repo/wiki)
- Examples: [Examples folder](./examples/)

## Changelog

### v1.0.0
- Initial release
- Gemini JSON integration
- Spaceplanning zero-touch nodes
- Design Automation support
- CPython3 compatibility

### v1.1.0 (Planned)
- Enhanced room shapes
- Multi-building support
- Advanced adjacency analysis
- Performance optimizations 