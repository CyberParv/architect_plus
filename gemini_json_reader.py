"""
Gemini JSON Reader for Spaceplanning Integration
Converts Gemini-generated architectural JSON to Spaceplanning data structures
"""

import json
import math
from typing import List, Dict, Any, Tuple, Optional

class GeminiJsonReader:
    """Reads and processes Gemini-generated JSON for architectural space planning"""
    
    def __init__(self, json_file_path: str):
        """Initialize with JSON file path"""
        self.json_file_path = json_file_path
        self.data = None
        self.load_json()
    
    def load_json(self) -> None:
        """Load JSON data from file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            self.data = {}
    
    def get_site_outline_points(self) -> List[Tuple[float, float]]:
        """Extract site outline points from JSON"""
        if not self.data or 'project' not in self.data:
            return [(0, 0), (100, 0), (100, 100), (0, 100)]  # Default rectangle
        
        site = self.data['project'].get('site', {})
        width = site.get('width', 100)
        depth = site.get('depth', 100)
        
        # Create rectangular site outline
        return [
            (0, 0),
            (width, 0),
            (width, depth),
            (0, depth)
        ]
    
    def get_building_outline_points(self, floor: int = 1) -> List[Tuple[float, float]]:
        """Get building outline for specific floor"""
        # For now, use site outline as building outline
        # Can be enhanced to support different building shapes per floor
        return self.get_site_outline_points()
    
    def get_department_data(self) -> List[Dict[str, Any]]:
        """Convert rooms to department data structure"""
        if not self.data or 'rooms' not in self.data:
            return []
        
        # Group rooms by department/function
        departments = {}
        for room in self.data['rooms']:
            dept_name = self._categorize_room(room['name'])
            if dept_name not in departments:
                departments[dept_name] = {
                    'name': dept_name,
                    'programs': [],
                    'total_area': 0,
                    'floor': room.get('floor', 1)
                }
            
            area = room['width'] * room['depth']
            departments[dept_name]['programs'].append({
                'id': len(departments[dept_name]['programs']) + 1,
                'name': room['name'],
                'area': area,
                'quantity': 1,
                'width': room['width'],
                'depth': room['depth'],
                'height': room.get('height', 3.0),
                'position': room.get('position', {'x': 0, 'y': 0, 'z': 0}),
                'shape': room.get('shape', 'rectangle'),
                'features': room.get('features', []),
                'adjacency_weight': self._calculate_adjacency_weight(room)
            })
            departments[dept_name]['total_area'] += area
        
        return list(departments.values())
    
    def _categorize_room(self, room_name: str) -> str:
        """Categorize room into department based on name"""
        room_name_lower = room_name.lower()
        
        if any(keyword in room_name_lower for keyword in ['emergency', 'trauma', 'triage']):
            return 'Emergency Department'
        elif any(keyword in room_name_lower for keyword in ['surgical', 'operating', 'surgery']):
            return 'Surgical Department'
        elif any(keyword in room_name_lower for keyword in ['patient', 'room', 'bed']):
            return 'Patient Care'
        elif any(keyword in room_name_lower for keyword in ['office', 'admin', 'reception']):
            return 'Administration'
        elif any(keyword in room_name_lower for keyword in ['lab', 'diagnostic', 'imaging']):
            return 'Diagnostic Services'
        elif any(keyword in room_name_lower for keyword in ['garden', 'healing', 'wellness']):
            return 'Wellness Areas'
        elif any(keyword in room_name_lower for keyword in ['cafeteria', 'dining', 'kitchen']):
            return 'Food Services'
        elif any(keyword in room_name_lower for keyword in ['parking', 'garage']):
            return 'Parking'
        else:
            return 'General Services'
    
    def _calculate_adjacency_weight(self, room: Dict[str, Any]) -> float:
        """Calculate adjacency weight based on room type and features"""
        base_weight = 1.0
        
        # High priority rooms
        if any(keyword in room['name'].lower() for keyword in ['emergency', 'trauma', 'surgical']):
            base_weight = 3.0
        elif any(keyword in room['name'].lower() for keyword in ['patient', 'room']):
            base_weight = 2.0
        elif any(keyword in room['name'].lower() for keyword in ['office', 'admin']):
            base_weight = 1.5
        
        # Adjust based on features
        features = room.get('features', [])
        if any('critical' in str(feature).lower() for feature in features):
            base_weight *= 1.5
        
        return base_weight
    
    def get_program_csv_data(self) -> List[List[str]]:
        """Generate CSV-like data structure for compatibility with original system"""
        departments = self.get_department_data()
        csv_data = []
        
        # Header
        csv_data.append([
            'ProgId', 'ProgramName', 'DeptName', 'Quantity', 
            'UnitArea', 'PrefValue', 'ColorCode', 'Type', 'Adjacency'
        ])
        
        prog_id = 1
        for dept in departments:
            for program in dept['programs']:
                csv_data.append([
                    str(prog_id),
                    program['name'],
                    dept['name'],
                    str(program['quantity']),
                    str(program['area']),
                    str(int(program['adjacency_weight'] * 10)),  # Convert to integer preference
                    str(prog_id % 10),  # Simple color coding
                    'regular',  # Type
                    dept['name']  # Adjacency to department
                ])
                prog_id += 1
        
        return csv_data
    
    def get_kpu_dimensions(self) -> Tuple[List[float], List[float]]:
        """Get KPU (Key Planning Unit) dimensions from room data"""
        departments = self.get_department_data()
        depths = []
        widths = []
        
        for dept in departments:
            for program in dept['programs']:
                depths.append(program['depth'])
                widths.append(program['width'])
        
        # If no data, return defaults
        if not depths or not widths:
            return [15.0, 20.0, 25.0], [10.0, 15.0, 20.0]
        
        # Return unique sorted values
        unique_depths = sorted(list(set(depths)))
        unique_widths = sorted(list(set(widths)))
        
        return unique_depths, unique_widths
    
    def get_circulation_factor(self) -> float:
        """Calculate circulation factor based on building type"""
        if not self.data or 'project' not in self.data:
            return 1.5
        
        project_name = self.data['project'].get('name', '').lower()
        
        # Hospital/medical buildings need more circulation
        if any(keyword in project_name for keyword in ['hospital', 'medical', 'clinic']):
            return 1.8
        # Office buildings
        elif any(keyword in project_name for keyword in ['office', 'corporate']):
            return 1.4
        # Retail/commercial
        elif any(keyword in project_name for keyword in ['retail', 'mall', 'shopping']):
            return 1.6
        # Residential
        elif any(keyword in project_name for keyword in ['residential', 'apartment', 'housing']):
            return 1.3
        
        return 1.5  # Default
    
    def get_building_height_info(self) -> Dict[str, Any]:
        """Get building height information"""
        if not self.data or 'project' not in self.data:
            return {'floors': 1, 'floor_height': 3.5, 'total_height': 3.5}
        
        floors = self.data['project'].get('floors', 1)
        
        # Calculate average floor height from room data
        floor_heights = []
        if 'rooms' in self.data:
            for room in self.data['rooms']:
                if 'height' in room:
                    floor_heights.append(room['height'])
        
        avg_floor_height = sum(floor_heights) / len(floor_heights) if floor_heights else 3.5
        total_height = floors * avg_floor_height
        
        return {
            'floors': floors,
            'floor_height': avg_floor_height,
            'total_height': total_height
        }
    
    def get_structural_elements(self) -> List[Dict[str, Any]]:
        """Extract structural elements from JSON"""
        if not self.data or 'structural' not in self.data:
            return []
        
        return self.data['structural']
    
    def get_walls_data(self) -> List[Dict[str, Any]]:
        """Extract walls data from JSON"""
        if not self.data or 'walls' not in self.data:
            return []
        
        return self.data['walls']
    
    def get_openings_data(self) -> List[Dict[str, Any]]:
        """Extract openings (doors/windows) data from JSON"""
        if not self.data or 'openings' not in self.data:
            return []
        
        return self.data['openings']
    
    def get_exterior_data(self) -> Dict[str, Any]:
        """Extract exterior/facade data from JSON"""
        if not self.data or 'exterior' not in self.data:
            return {}
        
        return self.data['exterior']
    
    def export_to_spaceplanning_format(self, output_path: str) -> None:
        """Export data in format compatible with original Spaceplanning system"""
        csv_data = self.get_program_csv_data()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            for row in csv_data:
                f.write(','.join(row) + '\n')
    
    def get_design_parameters(self) -> Dict[str, Any]:
        """Get all design parameters for Dynamo graph"""
        return {
            'site_outline': self.get_site_outline_points(),
            'building_outline': self.get_building_outline_points(),
            'departments': self.get_department_data(),
            'kpu_depths': self.get_kpu_dimensions()[0],
            'kpu_widths': self.get_kpu_dimensions()[1],
            'circulation_factor': self.get_circulation_factor(),
            'building_info': self.get_building_height_info(),
            'structural': self.get_structural_elements(),
            'walls': self.get_walls_data(),
            'openings': self.get_openings_data(),
            'exterior': self.get_exterior_data()
        }

# Test the reader
if __name__ == "__main__":
    reader = GeminiJsonReader("output/design.json")
    params = reader.get_design_parameters()
    print("Design Parameters:")
    for key, value in params.items():
        print(f"{key}: {value}") 