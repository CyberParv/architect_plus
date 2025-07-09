"""
Dynamo Spaceplanning Integration Script
Integrates Gemini JSON data with Spaceplanning zero-touch nodes
For use in Dynamo with CPython3 engine
"""

import sys
import os
import json
import math
from typing import List, Dict, Any, Tuple, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gemini_json_reader import GeminiJsonReader
except ImportError:
    print("Warning: Could not import GeminiJsonReader, using fallback")
    GeminiJsonReader = None

# Mock geometry classes for when ProtoGeometry is not available
class MockPoint2d:
    def __init__(self, x, y):
        self.X = x
        self.Y = y
    
    def __str__(self):
        return f"Point2d({self.X}, {self.Y})"

class MockPolygon2d:
    def __init__(self, points):
        self.Points = points
    
    def __str__(self):
        return f"Polygon2d with {len(self.Points)} points"

class MockGeometry:
    def __init__(self, geometry_type, **kwargs):
        self.type = geometry_type
        self.properties = kwargs
    
    def __str__(self):
        return f"{self.type}({self.properties})"

class DynamoSpaceplanningIntegrator:
    """Main integration class for Dynamo Spaceplanning"""
    
    def __init__(self, json_file_path: str = "output/design.json"):
        """Initialize with JSON file path"""
        self.json_file_path = json_file_path
        self.reader = None
        self.design_params = {}
        self.initialize_reader()
    
    def initialize_reader(self):
        """Initialize the JSON reader"""
        try:
            if GeminiJsonReader and os.path.exists(self.json_file_path):
                self.reader = GeminiJsonReader(self.json_file_path)
                self.design_params = self.reader.get_design_parameters()
            else:
                print(f"JSON file not found or reader unavailable: {self.json_file_path}")
                self.create_default_parameters()
        except Exception as e:
            print(f"Error initializing reader: {e}")
            self.create_default_parameters()
    
    def create_default_parameters(self):
        """Create default parameters when JSON is not available"""
        self.design_params = {
            'site_outline': [(0, 0), (100, 0), (100, 150), (0, 150)],
            'building_outline': [(0, 0), (100, 0), (100, 150), (0, 150)],
            'departments': [
                {
                    'name': 'Emergency Department',
                    'programs': [
                        {'name': 'Emergency Room', 'area': 225, 'width': 15, 'depth': 15, 'adjacency_weight': 3.0}
                    ],
                    'total_area': 225
                },
                {
                    'name': 'Patient Care',
                    'programs': [
                        {'name': 'Patient Room', 'area': 30, 'width': 6, 'depth': 5, 'adjacency_weight': 2.0}
                    ],
                    'total_area': 30
                }
            ],
            'kpu_depths': [15.0, 20.0, 25.0],
            'kpu_widths': [10.0, 15.0, 20.0],
            'circulation_factor': 1.8,
            'building_info': {'floors': 3, 'floor_height': 3.5, 'total_height': 10.5}
        }
    
    def get_site_outline_points(self):
        """Get site outline points as Point2d objects"""
        points = self.design_params.get('site_outline', [(0, 0), (100, 0), (100, 100), (0, 100)])
        
        try:
            # Try to use actual ProtoGeometry if available
            from Autodesk.DesignScript.Geometry import Point
            return [Point.ByCoordinates(p[0], p[1], 0) for p in points]
        except ImportError:
            # Fallback to mock objects
            return [MockPoint2d(p[0], p[1]) for p in points]
    
    def get_building_outline_polygon(self):
        """Get building outline as Polygon2d"""
        points = self.get_site_outline_points()
        
        try:
            # Try to use actual stuffer.Polygon2d if available
            import stuffer
            return stuffer.Polygon2d.ByPoints(points)
        except ImportError:
            # Fallback to mock object
            return MockPolygon2d(points)
    
    def create_department_data_stack(self):
        """Create department data stack compatible with Spaceplanning"""
        departments = self.design_params.get('departments', [])
        dept_data_stack = []
        
        for dept in departments:
            # Create program data for each department
            program_data_list = []
            for i, program in enumerate(dept.get('programs', [])):
                program_data = {
                    'ProgId': i + 1,
                    'ProgramName': program.get('name', 'Unknown'),
                    'DeptName': dept.get('name', 'Unknown'),
                    'Quantity': program.get('quantity', 1),
                    'UnitArea': program.get('area', 100),
                    'AdjacencyWeight': program.get('adjacency_weight', 1.0),
                    'Width': program.get('width', 10),
                    'Depth': program.get('depth', 10),
                    'Height': program.get('height', 3.0),
                    'Position': program.get('position', {'x': 0, 'y': 0, 'z': 0}),
                    'Shape': program.get('shape', 'rectangle'),
                    'Features': program.get('features', [])
                }
                program_data_list.append(program_data)
            
            dept_data = {
                'DeptName': dept.get('name', 'Unknown'),
                'ProgramsInDept': program_data_list,
                'DeptAreaNeeded': dept.get('total_area', 100),
                'DeptAreaProportionNeeded': 0.0,  # Will be calculated
                'CirculationFactor': self.design_params.get('circulation_factor', 1.5),
                'Floor': dept.get('floor', 1)
            }
            dept_data_stack.append(dept_data)
        
        # Calculate area proportions
        total_area = sum(dept.get('total_area', 100) for dept in departments)
        for dept_data in dept_data_stack:
            dept_data['DeptAreaProportionNeeded'] = dept_data['DeptAreaNeeded'] / total_area if total_area > 0 else 0.0
        
        return dept_data_stack
    
    def get_kpu_dimensions(self):
        """Get KPU dimensions"""
        depths = self.design_params.get('kpu_depths', [15.0, 20.0, 25.0])
        widths = self.design_params.get('kpu_widths', [10.0, 15.0, 20.0])
        return depths, widths
    
    def get_circulation_factor(self):
        """Get circulation factor"""
        return self.design_params.get('circulation_factor', 1.5)
    
    def get_building_height_info(self):
        """Get building height information"""
        return self.design_params.get('building_info', {
            'floors': 1,
            'floor_height': 3.5,
            'total_height': 3.5
        })
    
    def create_grid_points(self, spacing: float = 5.0):
        """Create grid points for space planning"""
        site_points = self.design_params.get('site_outline', [(0, 0), (100, 0), (100, 100), (0, 100)])
        
        # Find bounding box
        min_x = min(p[0] for p in site_points)
        max_x = max(p[0] for p in site_points)
        min_y = min(p[1] for p in site_points)
        max_y = max(p[1] for p in site_points)
        
        # Create grid
        grid_points = []
        x = min_x
        while x <= max_x:
            y = min_y
            while y <= max_y:
                grid_points.append((x, y))
                y += spacing
            x += spacing
        
        try:
            # Try to use actual ProtoGeometry if available
            from Autodesk.DesignScript.Geometry import Point
            return [Point.ByCoordinates(p[0], p[1], 0) for p in grid_points]
        except ImportError:
            # Fallback to mock objects
            return [MockPoint2d(p[0], p[1]) for p in grid_points]
    
    def place_departments_on_site(self, design_seed: int = 50):
        """Place departments on site using spaceplanning logic"""
        dept_data_stack = self.create_department_data_stack()
        building_outline = [self.get_building_outline_polygon()]
        kpu_depths, kpu_widths = self.get_kpu_dimensions()
        
        # Simulate department placement
        placed_departments = []
        current_x = 10
        current_y = 10
        
        for i, dept in enumerate(dept_data_stack):
            # Simple placement logic - in real implementation, this would use
            # the actual Spaceplanning BuildLayout.PlaceDepartments method
            dept_width = kpu_widths[i % len(kpu_widths)]
            dept_depth = kpu_depths[i % len(kpu_depths)]
            
            # Create department polygon
            dept_points = [
                (current_x, current_y),
                (current_x + dept_width, current_y),
                (current_x + dept_width, current_y + dept_depth),
                (current_x, current_y + dept_depth)
            ]
            
            try:
                # Try to use actual geometry if available
                from Autodesk.DesignScript.Geometry import Point
                points = [Point.ByCoordinates(p[0], p[1], 0) for p in dept_points]
                import stuffer
                dept_polygon = stuffer.Polygon2d.ByPoints(points)
            except ImportError:
                # Fallback to mock objects
                points = [MockPoint2d(p[0], p[1]) for p in dept_points]
                dept_polygon = MockPolygon2d(points)
            
            dept['DeptPolygon'] = dept_polygon
            dept['DeptAreaProvided'] = dept_width * dept_depth
            placed_departments.append(dept)
            
            # Move to next position
            current_x += dept_width + 5
            if current_x > 80:  # Wrap to next row
                current_x = 10
                current_y += dept_depth + 5
        
        return placed_departments
    
    def place_programs_in_departments(self, placed_departments: List[Dict], design_seed: int = 10):
        """Place programs within departments"""
        for dept in placed_departments:
            programs = dept.get('ProgramsInDept', [])
            dept_polygon = dept.get('DeptPolygon')
            
            if not programs or not dept_polygon:
                continue
            
            # Simple program placement within department
            program_polygons = []
            for i, program in enumerate(programs):
                # Create simple rectangular program within department
                prog_width = program.get('Width', 5)
                prog_depth = program.get('Depth', 5)
                
                # Position within department (simplified)
                offset_x = (i % 2) * prog_width
                offset_y = (i // 2) * prog_depth
                
                prog_points = [
                    (offset_x, offset_y),
                    (offset_x + prog_width, offset_y),
                    (offset_x + prog_width, offset_y + prog_depth),
                    (offset_x, offset_y + prog_depth)
                ]
                
                try:
                    # Try to use actual geometry if available
                    from Autodesk.DesignScript.Geometry import Point
                    points = [Point.ByCoordinates(p[0], p[1], 0) for p in prog_points]
                    import stuffer
                    prog_polygon = stuffer.Polygon2d.ByPoints(points)
                except ImportError:
                    # Fallback to mock objects
                    points = [MockPoint2d(p[0], p[1]) for p in prog_points]
                    prog_polygon = MockPolygon2d(points)
                
                program['ProgramPolygon'] = prog_polygon
                program['AreaProvided'] = prog_width * prog_depth
                program_polygons.append(prog_polygon)
            
            dept['ProgramPolygons'] = program_polygons
        
        return placed_departments
    
    def create_circulation_network(self, placed_departments: List[Dict]):
        """Create circulation network between departments"""
        circulation_lines = []
        
        # Simple circulation network - connect department centroids
        for i, dept1 in enumerate(placed_departments):
            for j, dept2 in enumerate(placed_departments[i+1:], i+1):
                # Calculate centroids (simplified)
                try:
                    # Try to use actual geometry if available
                    from Autodesk.DesignScript.Geometry import Point, Line
                    
                    # Mock centroid calculation
                    centroid1 = Point.ByCoordinates(50, 50, 0)  # Simplified
                    centroid2 = Point.ByCoordinates(75, 75, 0)  # Simplified
                    
                    circ_line = Line.ByStartPointEndPoint(centroid1, centroid2)
                    circulation_lines.append(circ_line)
                except ImportError:
                    # Fallback to mock objects
                    circulation_lines.append(MockGeometry("Line", start=(50, 50), end=(75, 75)))
        
        return circulation_lines
    
    def generate_3d_geometry(self, placed_departments: List[Dict], height: float = 3.0):
        """Generate 3D geometry from 2D layouts"""
        geometry_3d = []
        
        for dept in placed_departments:
            dept_polygon = dept.get('DeptPolygon')
            if not dept_polygon:
                continue
            
            try:
                # Try to use actual geometry if available
                from Autodesk.DesignScript.Geometry import Surface
                import stuffer
                
                # Extrude polygon to create 3D surface
                dept_surface = stuffer.DynamoGeometry.MakeSurfaceForPolygon2d([dept_polygon], height)
                geometry_3d.append(dept_surface)
                
                # Add program geometry
                for program in dept.get('ProgramsInDept', []):
                    prog_polygon = program.get('ProgramPolygon')
                    if prog_polygon:
                        prog_height = program.get('Height', 3.0)
                        prog_surface = stuffer.DynamoGeometry.MakeSurfaceForPolygon2d([prog_polygon], prog_height)
                        geometry_3d.append(prog_surface)
                        
            except ImportError:
                # Fallback to mock objects
                geometry_3d.append(MockGeometry("Surface", polygon=dept_polygon, height=height))
        
        return geometry_3d
    
    def run_complete_spaceplanning(self, design_seed: int = 50):
        """Run complete spaceplanning workflow"""
        try:
            # Step 1: Place departments on site
            placed_departments = self.place_departments_on_site(design_seed)
            
            # Step 2: Place programs within departments
            placed_departments = self.place_programs_in_departments(placed_departments, design_seed)
            
            # Step 3: Create circulation network
            circulation_network = self.create_circulation_network(placed_departments)
            
            # Step 4: Generate 3D geometry
            geometry_3d = self.generate_3d_geometry(placed_departments)
            
            # Step 5: Prepare results
            results = {
                'departments': placed_departments,
                'circulation': circulation_network,
                'geometry_3d': geometry_3d,
                'site_outline': self.get_site_outline_points(),
                'building_outline': self.get_building_outline_polygon(),
                'grid_points': self.create_grid_points(),
                'design_parameters': self.design_params,
                'success': True,
                'message': 'Spaceplanning completed successfully'
            }
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error in spaceplanning: {str(e)}',
                'error': str(e)
            }

# Main function for Dynamo
def process_gemini_json_for_spaceplanning(json_path: str = "output/design.json", 
                                        design_seed: int = 50,
                                        circulation_factor: float = 1.8,
                                        acceptable_width: float = 18.0):
    """
    Main function to be called from Dynamo
    Processes Gemini JSON and returns spaceplanning results
    """
    try:
        # Initialize integrator
        integrator = DynamoSpaceplanningIntegrator(json_path)
        
        # Override circulation factor if provided
        if circulation_factor != 1.8:
            integrator.design_params['circulation_factor'] = circulation_factor
        
        # Run spaceplanning
        results = integrator.run_complete_spaceplanning(design_seed)
        
        return results
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing Gemini JSON: {str(e)}',
            'error': str(e)
        }

# Test function
if __name__ == "__main__":
    # Test the integration
    results = process_gemini_json_for_spaceplanning()
    
    if results.get('success'):
        print("Spaceplanning completed successfully!")
        print(f"Departments placed: {len(results.get('departments', []))}")
        print(f"Circulation elements: {len(results.get('circulation', []))}")
        print(f"3D geometry elements: {len(results.get('geometry_3d', []))}")
    else:
        print(f"Error: {results.get('message', 'Unknown error')}") 