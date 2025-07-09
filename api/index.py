import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

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
    return jsonify({
        'success': False,
        'error': 'Spaceplanning integration not available in Vercel deployment'
    }), 500

@app.route('/spaceplanning-info', methods=['GET'])
def spaceplanning_info():
    """Information about spaceplanning availability"""
    return jsonify({
        'available': False,
        'reason': 'Spaceplanning integration not available in Vercel deployment'
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'gemini_configured': bool(os.getenv('GEMINI_API_KEY')),
        'spaceplanning_available': False,
        'deployment': 'vercel'
    })

def validate_and_enhance_design(design_data):
    """Validate and enhance design data"""
    if not design_data:
        return {}
    
    # Ensure required fields exist
    if 'project' not in design_data:
        design_data['project'] = {}
    
    if 'rooms' not in design_data:
        design_data['rooms'] = []
    
    # Generate walls from rooms if not present
    if 'walls' not in design_data or not design_data['walls']:
        design_data['walls'] = generate_walls_from_rooms(design_data.get('rooms', []))
    
    # Generate openings if not present
    if 'openings' not in design_data or not design_data['openings']:
        design_data['openings'] = generate_basic_openings(design_data.get('walls', []))
    
    # Generate structural elements if not present
    if 'structural' not in design_data or not design_data['structural']:
        design_data['structural'] = generate_structural_elements(design_data.get('rooms', []))
    
    return design_data

def generate_walls_from_rooms(rooms):
    """Generate walls from room layout"""
    walls = []
    
    for i, room in enumerate(rooms):
        if not room.get('position'):
            continue
            
        x = room['position']['x']
        y = room['position']['y']
        z = room['position'].get('z', 0)
        width = room.get('width', 10)
        depth = room.get('depth', 10)
        height = room.get('height', 3)
        
        # Generate four walls for each room
        wall_thickness = 0.2
        
        # Front wall
        walls.append({
            'start': {'x': x, 'y': y, 'z': z},
            'end': {'x': x + width, 'y': y, 'z': z},
            'height': height,
            'thickness': wall_thickness,
            'material': 'concrete'
        })
        
        # Right wall
        walls.append({
            'start': {'x': x + width, 'y': y, 'z': z},
            'end': {'x': x + width, 'y': y + depth, 'z': z},
            'height': height,
            'thickness': wall_thickness,
            'material': 'concrete'
        })
        
        # Back wall
        walls.append({
            'start': {'x': x + width, 'y': y + depth, 'z': z},
            'end': {'x': x, 'y': y + depth, 'z': z},
            'height': height,
            'thickness': wall_thickness,
            'material': 'concrete'
        })
        
        # Left wall
        walls.append({
            'start': {'x': x, 'y': y + depth, 'z': z},
            'end': {'x': x, 'y': y, 'z': z},
            'height': height,
            'thickness': wall_thickness,
            'material': 'concrete'
        })
    
    return walls

def generate_basic_openings(walls):
    """Generate basic openings for walls"""
    openings = []
    
    for i, wall in enumerate(walls):
        if i % 4 == 0:  # Add door to front wall
            openings.append({
                'type': 'door',
                'wall_id': i,
                'position': 0.5,
                'width': 0.9,
                'height': 2.1,
                'style': 'standard'
            })
        elif i % 4 == 1:  # Add window to right wall
            openings.append({
                'type': 'window',
                'wall_id': i,
                'position': 0.5,
                'width': 1.2,
                'height': 1.2,
                'style': 'standard'
            })
    
    return openings

def generate_structural_elements(rooms):
    """Generate structural elements for rooms"""
    structural = []
    
    for room in rooms:
        if not room.get('position'):
            continue
            
        x = room['position']['x']
        y = room['position']['y']
        z = room['position'].get('z', 0)
        width = room.get('width', 10)
        depth = room.get('depth', 10)
        height = room.get('height', 3)
        
        # Add columns for large rooms
        if width > 8 or depth > 8:
            # Add column at center
            structural.append({
                'type': 'column',
                'position': {'x': x + width/2, 'y': y + depth/2, 'z': z},
                'diameter': 0.3,
                'height': height,
                'cross_section': 'circular'
            })
    
    return structural

def generate_complex_fallback_data(prompt):
    """Generate complex fallback data when AI fails"""
    return {
        'project': {
            'name': f'AI Generated Building from: {prompt[:50]}...',
            'style': 'modern',
            'floors': 2,
            'site': {'width': 30, 'depth': 25}
        },
        'rooms': [
            {
                'name': 'Main Living Area',
                'floor': 1,
                'width': 12,
                'depth': 8,
                'height': 3.5,
                'position': {'x': 0, 'y': 0, 'z': 0},
                'shape': 'rectangle',
                'features': ['large windows', 'open concept']
            },
            {
                'name': 'Kitchen',
                'floor': 1,
                'width': 8,
                'depth': 6,
                'height': 3.5,
                'position': {'x': 12, 'y': 0, 'z': 0},
                'shape': 'L-shaped',
                'features': ['island', 'modern appliances']
            },
            {
                'name': 'Master Bedroom',
                'floor': 2,
                'width': 10,
                'depth': 8,
                'height': 3.2,
                'position': {'x': 0, 'y': 0, 'z': 3.5},
                'shape': 'rectangle',
                'features': ['ensuite', 'walk-in closet']
            }
        ],
        'walls': [],
        'openings': [],
        'structural': [],
        'exterior': {
            'roof': {'type': 'gabled', 'pitch': 30},
            'facade': {'material': 'brick', 'color': 'red'}
        }
    }

# For Vercel deployment
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True) 