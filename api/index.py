import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Configure Google Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("Warning: GEMINI_API_KEY environment variable not set")
else:
    genai.configure(api_key=api_key)

# Initialize the model only if API key is available
model = None
if api_key:
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        print(f"Error initializing Gemini model: {e}")

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
@app.route('/generate-design', methods=['POST'])
def generate_design():
    try:
        if not model:
            return jsonify({
                'success': False,
                'error': 'Gemini API not configured. Please set GEMINI_API_KEY environment variable.'
            }), 500

        prompt = request.json.get('prompt', '') or request.json.get('description', '')
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Please provide a description for your architectural design.'
            }), 400

        # Enhanced prompt for architectural design
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
            "structural": [
                {{
                    "type": "column/beam",
                    "position": {{"x": x, "y": y, "z": z}},
                    "diameter": diameter_for_column,
                    "height": height_for_column
                }}
            ],
            "exterior": {{
                "roof": {{"type": "gabled/hip/flat", "pitch": roof_pitch_degrees}},
                "facade": {{"material": "brick/glass/concrete", "color": "color_name"}}
            }}
        }}
        
        Requirements:
        1. Create realistic room dimensions (3-12 meters width/depth, 2.5-4 meters height)
        2. Position rooms logically (avoid overlaps, create functional layouts)
        3. Include appropriate structural elements for larger spans
        4. Make the design buildable and structurally sound
        
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
            # Fallback to sample data
            design_data = generate_fallback_data(prompt)
        
        return jsonify({
            'success': True,
            'design': design_data,
            'message': 'Architectural design generated successfully!'
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gemini_configured': bool(api_key),
        'version': '1.0.0',
        'deployment': 'vercel'
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
    
    return design_data

def generate_fallback_data(prompt):
    """Generate fallback data when AI fails"""
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
            }
        ],
        'walls': [
            {
                'start': {'x': 0, 'y': 0, 'z': 0},
                'end': {'x': 14, 'y': 0, 'z': 0},
                'height': 3.5,
                'thickness': 0.2,
                'material': 'concrete'
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

# For Vercel deployment
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)