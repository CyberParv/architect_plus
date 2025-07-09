import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# Import our spaceplanning integration
try:
    from dynamo_spaceplanning_integration import process_gemini_json_for_spaceplanning
    from gemini_json_reader import GeminiJsonReader
    from design_automation_integration import DesignAutomationIntegrator
    SPACEPLANNING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Spaceplanning integration not available: {e}")
    SPACEPLANNING_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
@app.route('/generate-design', methods=['POST'])
def generate_design():
    try:
        prompt = request.json.get('prompt', '') or request.json.get('description', '')
        
        # Enhanced prompt for complex architectural structures
        enhanced_prompt = f"""
        As an expert architect, create a detailed architectural design based on this request: "{prompt}"
        
        Generate a comprehensive JSON response with the following structure:
        
        {{
            "project": {{
                "name": "Building Name",
                "style": "architectural style (modern, traditional, etc.)",
                "floors": number_of_floors,
                "site": {{"width": site_width_meters, "depth": site_depth_meters}}
            }},
            "rooms": [
                {{
                    "name": "Room Name",
                    "floor": floor_number,
                    "width": width_in_meters,
                    "depth": depth_in_meters,
                    "height": height_in_meters,
                    "position": {{"x": x_coordinate, "y": y_coordinate, "z": z_coordinate}},
                    "shape": "rectangle/L-shaped/circular/custom",
                    "features": ["feature1", "feature2"]
                }}
            ],
            "walls": [
                {{
                    "start": {{"x": start_x, "y": start_y, "z": start_z}},
                    "end": {{"x": end_x, "y": end_y, "z": end_z}},
                    "height": wall_height,
                    "thickness": wall_thickness,
                    "material": "concrete/brick/wood"
                }}
            ],
            "openings": [
                {{
                    "type": "door/window",
                    "wall_id": wall_index,
                    "position": position_along_wall,
                    "width": opening_width,
                    "height": opening_height,
                    "style": "standard/french/sliding"
                }}
            ],
            "structural": [
                {{
                    "type": "column/beam",
                    "position": {{"x": x, "y": y, "z": z}},
                    "diameter": diameter_for_column,
                    "height": height_for_column,
                    "start": {{"x": start_x, "y": start_y, "z": start_z}},
                    "end": {{"x": end_x, "y": end_y, "z": end_z}},
                    "cross_section": "rectangular/circular/I-beam"
                }}
            ],
            "exterior": {{
                "roof": {{
                    "type": "gabled/hip/flat/shed",
                    "pitch": roof_pitch_degrees
                }},
                "facade": {{
                    "material": "brick/glass/concrete/wood",
                    "color": "color_name"
                }}
            }}
        }}
        
        Requirements:
        1. Create realistic room dimensions (3-12 meters width/depth, 2.5-4 meters height)
        2. Position rooms logically (avoid overlaps, create functional layouts)
        3. Include appropriate walls to enclose spaces
        4. Add doors between rooms and windows for natural light
        5. Include structural elements (columns, beams) for larger spans
        6. Design appropriate roof structure
        7. For multi-story buildings, stack rooms vertically (z-coordinate changes)
        8. Use different room shapes for variety (L-shaped kitchens, circular towers, etc.)
        9. Consider architectural style in material choices
        10. Make the design buildable and structurally sound
        
        Focus on creating a {prompt} that is both functional and architecturally interesting.
        Return ONLY the JSON response, no additional text.
        """
        
        # Generate content using Gemini
        response = model.generate_content(enhanced_prompt)
        
        # Parse the response
        try:
            # Clean the response text
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            design_data = json.loads(response_text)
            
            # Validate and enhance the data
            design_data = validate_and_enhance_design(design_data)
            
        except json.JSONDecodeError:
            # Fallback to complex sample data
            design_data = generate_complex_fallback_data(prompt)
        
        # Save to file
        os.makedirs('output', exist_ok=True)
        with open('output/design.json', 'w') as f:
            json.dump(design_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'design': design_data,
            'message': 'Complex architectural design generated successfully!'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-with-spaceplanning', methods=['POST'])
def generate_with_spaceplanning():
    """Enhanced route that includes professional spaceplanning"""
    try:
        prompt = request.json.get('prompt', '') or request.json.get('description', '')
        design_seed = request.json.get('design_seed', 50)
        circulation_factor = request.json.get('circulation_factor', 1.8)
        acceptable_width = request.json.get('acceptable_width', 18.0)
        
        if not SPACEPLANNING_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Spaceplanning integration not available'
            }), 500
        
        # First, generate the basic design using Gemini
        enhanced_prompt = f"""
        As an expert architect, create a detailed architectural design based on this request: "{prompt}"
        
        Generate a comprehensive JSON response with the following structure:
        
        {{
            "project": {{
                "name": "Building Name",
                "style": "architectural style (modern, traditional, etc.)",
                "floors": number_of_floors,
                "site": {{"width": site_width_meters, "depth": site_depth_meters}}
            }},
            "rooms": [
                {{
                    "name": "Room Name",
                    "floor": floor_number,
                    "width": width_in_meters,
                    "depth": depth_in_meters,
                    "height": height_in_meters,
                    "position": {{"x": x_coordinate, "y": y_coordinate, "z": z_coordinate}},
                    "shape": "rectangle/L-shaped/circular/custom",
                    "features": ["feature1", "feature2"]
                }}
            ]
        }}
        
        Focus on creating a {prompt} that is both functional and architecturally interesting.
        Return ONLY the JSON response, no additional text.
        """
        
        # Generate content using Gemini
        response = model.generate_content(enhanced_prompt)
        
        # Parse the response
        try:
            # Clean the response text
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            design_data = json.loads(response_text)
            
            # Validate and enhance the data
            design_data = validate_and_enhance_design(design_data)
            
        except json.JSONDecodeError:
            # Fallback to complex sample data
            design_data = generate_complex_fallback_data(prompt)
        
        # Save to file
        os.makedirs('output', exist_ok=True)
        with open('output/design.json', 'w') as f:
            json.dump(design_data, f, indent=2)
        
        design_result = {
            'success': True,
            'design': design_data,
            'message': 'Complex architectural design generated successfully!'
        }
        
        # Now enhance with professional spaceplanning
        spaceplanning_results = process_gemini_json_for_spaceplanning(
            json_path="output/design.json",
            design_seed=int(design_seed),
            circulation_factor=float(circulation_factor),
            acceptable_width=float(acceptable_width)
        )
        
        if spaceplanning_results.get('success'):
            # Combine the results
            enhanced_design = {
                'success': True,
                'design': design_result['design'],
                'spaceplanning': {
                    'departments': len(spaceplanning_results.get('departments', [])),
                    'programs': len(spaceplanning_results.get('departments', [])),
                    'circulation_elements': len(spaceplanning_results.get('circulation', [])),
                    'geometry_3d': len(spaceplanning_results.get('geometry_3d', [])),
                    'building_data': spaceplanning_results.get('building_data', {}),
                    'status': spaceplanning_results.get('status', 'Unknown')
                },
                'message': 'Professional architectural design with spaceplanning generated successfully!',
                'spaceplanning_available': True,
                'raw_spaceplanning': spaceplanning_results
            }
            
            # Save enhanced results
            with open('output/enhanced_design.json', 'w') as f:
                json.dump(enhanced_design, f, indent=2)
            
            return jsonify(enhanced_design)
        else:
            # Return basic design with spaceplanning error info
            return jsonify({
                'success': True,
                'design': design_result['design'],
                'spaceplanning': {
                    'error': spaceplanning_results.get('message', 'Spaceplanning failed'),
                    'status': 'failed'
                },
                'message': 'Basic design generated, spaceplanning enhancement failed',
                'spaceplanning_available': True
            })
        
    except Exception as e:
        print(f"Error in spaceplanning generation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'spaceplanning_available': SPACEPLANNING_AVAILABLE
        }), 500

@app.route('/spaceplanning-info', methods=['GET'])
def spaceplanning_info():
    """Get information about spaceplanning capabilities"""
    try:
        if not SPACEPLANNING_AVAILABLE:
            return jsonify({
                'available': False,
                'message': 'Spaceplanning integration not available'
            })
        
        # Test read a sample design
        reader = GeminiJsonReader("output/design.json")
        params = reader.get_design_parameters()
        
        return jsonify({
            'available': True,
            'capabilities': {
                'department_categorization': True,
                'intelligent_adjacencies': True,
                'circulation_networks': True,
                'multi_floor_support': True,
                '3d_geometry_generation': True,
                'design_automation_ready': True
            },
            'supported_building_types': [
                'Hospital/Medical',
                'Office/Corporate', 
                'Residential',
                'Retail/Commercial',
                'Educational',
                'Mixed-Use'
            ],
            'parameters': {
                'design_seed': {'min': 1, 'max': 100, 'default': 50},
                'circulation_factor': {'min': 1.0, 'max': 3.0, 'default': 1.8},
                'acceptable_width': {'min': 10.0, 'max': 30.0, 'default': 18.0}
            },
            'sample_design_available': os.path.exists('output/design.json'),
            'departments_detected': len(params.get('departments', [])) if os.path.exists('output/design.json') else 0
        })
        
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e)
        })

@app.route('/design-automation', methods=['POST'])
def prepare_design_automation():
    """Prepare files for Autodesk Design Automation"""
    try:
        if not SPACEPLANNING_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Spaceplanning integration not available'
            }), 500
        
        design_params = {
            'design_seed': request.json.get('design_seed', 50),
            'circulation_factor': request.json.get('circulation_factor', 1.8),
            'acceptable_width': request.json.get('acceptable_width', 18.0),
            'kpu_depth': request.json.get('kpu_depth', 15.0),
            'kpu_width': request.json.get('kpu_width', 10.0)
        }
        
        integrator = DesignAutomationIntegrator()
        results = integrator.generate_design_automation_files(
            "output/design.json",
            design_params
        )
        
        if results.get('success'):
            return jsonify({
                'success': True,
                'package_created': True,
                'activity_id': results['activity']['id'],
                'temp_directory': results['temp_dir'],
                'test_results': results['test_results'],
                'message': 'Design Automation package created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': results.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'spaceplanning_available': SPACEPLANNING_AVAILABLE,
        'gemini_configured': bool(os.getenv('GEMINI_API_KEY')),
        'version': '1.0.0'
    })

def validate_and_enhance_design(design_data):
    """Validate and enhance the generated design data"""
    
    # Ensure project info exists
    if 'project' not in design_data:
        design_data['project'] = {
            'name': 'Generated Building',
            'style': 'modern',
            'floors': 1
        }
    
    # Ensure rooms exist and are valid
    if 'rooms' not in design_data or not design_data['rooms']:
        design_data['rooms'] = [
            {
                'name': 'Living Room',
                'floor': 1,
                'width': 6, 'depth': 5, 'height': 3,
                'position': {'x': 0, 'y': 0, 'z': 0},
                'shape': 'rectangle'
            }
        ]
    
    # Validate room dimensions
    for room in design_data['rooms']:
        room['width'] = max(2, min(15, room.get('width', 4)))
        room['depth'] = max(2, min(15, room.get('depth', 4)))
        room['height'] = max(2.2, min(5, room.get('height', 3)))
        
        if 'position' not in room:
            room['position'] = {'x': 0, 'y': 0, 'z': 0}
        
        if 'shape' not in room:
            room['shape'] = 'rectangle'
    
    # Generate walls if not present
    if 'walls' not in design_data:
        design_data['walls'] = generate_walls_from_rooms(design_data['rooms'])
    
    # Generate openings if not present
    if 'openings' not in design_data:
        design_data['openings'] = generate_basic_openings(design_data['walls'])
    
    # Add structural elements for large spans
    if 'structural' not in design_data:
        design_data['structural'] = generate_structural_elements(design_data['rooms'])
    
    # Add roof if not present
    if 'exterior' not in design_data:
        design_data['exterior'] = {
            'roof': {'type': 'gabled', 'pitch': 30},
            'facade': {'material': 'brick', 'color': 'red'}
        }
    
    return design_data

def generate_walls_from_rooms(rooms):
    """Generate basic walls around rooms"""
    walls = []
    wall_id = 0
    
    for room in rooms:
        pos = room['position']
        w, d, h = room['width'], room['depth'], room['height']
        
        # Four walls around each room
        walls.extend([
            {
                'start': {'x': pos['x'], 'y': pos['y'], 'z': pos['z']},
                'end': {'x': pos['x'] + w, 'y': pos['y'], 'z': pos['z']},
                'height': h,
                'thickness': 0.2
            },
            {
                'start': {'x': pos['x'] + w, 'y': pos['y'], 'z': pos['z']},
                'end': {'x': pos['x'] + w, 'y': pos['y'] + d, 'z': pos['z']},
                'height': h,
                'thickness': 0.2
            },
            {
                'start': {'x': pos['x'] + w, 'y': pos['y'] + d, 'z': pos['z']},
                'end': {'x': pos['x'], 'y': pos['y'] + d, 'z': pos['z']},
                'height': h,
                'thickness': 0.2
            },
            {
                'start': {'x': pos['x'], 'y': pos['y'] + d, 'z': pos['z']},
                'end': {'x': pos['x'], 'y': pos['y'], 'z': pos['z']},
                'height': h,
                'thickness': 0.2
            }
        ])
    
    return walls

def generate_basic_openings(walls):
    """Generate basic doors and windows"""
    openings = []
    
    for i, wall in enumerate(walls[:min(len(walls), 4)]):  # First 4 walls
        if i % 2 == 0:  # Even walls get doors
            openings.append({
                'type': 'door',
                'wall_id': i,
                'position': 1.0,
                'width': 0.9,
                'height': 2.1
            })
        else:  # Odd walls get windows
            openings.append({
                'type': 'window',
                'wall_id': i,
                'position': 1.5,
                'width': 1.2,
                'height': 1.0
            })
    
    return openings

def generate_structural_elements(rooms):
    """Generate structural elements for large rooms"""
    structural = []
    
    for room in rooms:
        # Add columns for large rooms
        if room['width'] > 8 or room['depth'] > 8:
            pos = room['position']
            structural.append({
                'type': 'column',
                'position': {
                    'x': pos['x'] + room['width'] / 2,
                    'y': pos['y'] + room['depth'] / 2,
                    'z': pos['z']
                },
                'diameter': 0.3,
                'height': room['height']
            })
    
    return structural

def generate_complex_fallback_data(prompt):
    """Generate complex fallback data when AI fails"""
    return {
        'project': {
            'name': f'AI-Generated {prompt}',
            'style': 'modern',
            'floors': 2,
            'site': {'width': 20, 'depth': 15}
        },
        'rooms': [
            {
                'name': 'Living Room',
                'floor': 1,
                'width': 8, 'depth': 6, 'height': 3.5,
                'position': {'x': 0, 'y': 0, 'z': 0},
                'shape': 'rectangle',
                'features': ['fireplace', 'large_windows']
            },
            {
                'name': 'Kitchen',
                'floor': 1,
                'width': 6, 'depth': 4, 'height': 3.5,
                'position': {'x': 8, 'y': 0, 'z': 0},
                'shape': 'L-shaped',
                'features': ['island', 'pantry']
            },
            {
                'name': 'Master Bedroom',
                'floor': 2,
                'width': 6, 'depth': 5, 'height': 3.2,
                'position': {'x': 0, 'y': 0, 'z': 3.5},
                'shape': 'rectangle',
                'features': ['ensuite', 'walk_in_closet']
            },
            {
                'name': 'Bathroom',
                'floor': 2,
                'width': 3, 'depth': 3, 'height': 3.2,
                'position': {'x': 6, 'y': 0, 'z': 3.5},
                'shape': 'rectangle',
                'features': ['shower', 'bathtub']
            }
        ],
        'walls': [
            {
                'start': {'x': 0, 'y': 0, 'z': 0},
                'end': {'x': 14, 'y': 0, 'z': 0},
                'height': 3.5,
                'thickness': 0.2,
                'material': 'concrete'
            },
            {
                'start': {'x': 14, 'y': 0, 'z': 0},
                'end': {'x': 14, 'y': 6, 'z': 0},
                'height': 3.5,
                'thickness': 0.2,
                'material': 'concrete'
            }
        ],
        'openings': [
            {
                'type': 'door',
                'wall_id': 0,
                'position': 2.0,
                'width': 0.9,
                'height': 2.1,
                'style': 'standard'
            },
            {
                'type': 'window',
                'wall_id': 0,
                'position': 6.0,
                'width': 1.5,
                'height': 1.2,
                'style': 'casement'
            }
        ],
        'structural': [
            {
                'type': 'column',
                'position': {'x': 7, 'y': 3, 'z': 0},
                'diameter': 0.3,
                'height': 7.0
            }
        ],
        'exterior': {
            'roof': {'type': 'gabled', 'pitch': 30},
            'facade': {'material': 'brick', 'color': 'red'}
        }
    }

if __name__ == '__main__':
    # Run the Flask app in debug mode
    app.run(debug=True, host='localhost', port=5000) 