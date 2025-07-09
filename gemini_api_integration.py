#!/usr/bin/env python3
"""
Gemini API Integration for Architect Plus
Real API integration for architectural design generation
"""

import json
import requests
import sys

def call_gemini_api(prompt, api_key):
    """
    Real Gemini API call for architectural design generation
    """
    
    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    # Enhanced architectural prompt
    enhanced_prompt = f"""
    You are a professional architect and building designer. Generate a detailed architectural design based on this request: "{prompt}"
    
    Provide your response as a JSON object with this exact structure:
    {{
        "building_type": "Building name/type",
        "floors": number_of_floors,
        "style": "Architectural style",
        "features": ["feature1", "feature2", "feature3"],
        "rooms": [
            {{
                "name": "Room name",
                "floor": floor_number,
                "type": "room_category",
                "width": width_in_meters,
                "depth": depth_in_meters,
                "height": height_in_meters,
                "x": x_position,
                "y": y_position,
                "z": z_position,
                "shape": "rectangle/circle/l_shaped"
            }}
        ],
        "structural_elements": [
            {{
                "name": "Element name",
                "type": "column/facade/skylight",
                "positions": [[x1, y1], [x2, y2]],
                "height": height_or_size
            }}
        ]
    }}
    
    Guidelines:
    - Use realistic dimensions (rooms 3-15m wide/deep, 2.5-5m high)
    - Position rooms to avoid overlap (spread along x, y, z axes)
    - Include 8-15 rooms for a complete building
    - Add structural elements (columns, facades, skylights)
    - Consider sustainable features (solar panels, green roofs)
    - Use professional architectural terminology
    - Ensure floor numbers are logical (0=ground, 1=first floor, etc.)
    
    Return ONLY the JSON object, no additional text.
    """
    
    # Request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": enhanced_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 2048
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make API call
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract generated text
            if 'candidates' in result and len(result['candidates']) > 0:
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                
                # Try to parse as JSON
                try:
                    # Clean up the response (remove any markdown formatting)
                    cleaned_text = generated_text.strip()
                    if cleaned_text.startswith('```json'):
                        cleaned_text = cleaned_text[7:]
                    if cleaned_text.endswith('```'):
                        cleaned_text = cleaned_text[:-3]
                    
                    design_data = json.loads(cleaned_text)
                    return design_data
                    
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON response: {generated_text}")
                    return get_fallback_design(prompt)
            else:
                print("No candidates in API response")
                return get_fallback_design(prompt)
        else:
            print(f"API Error {response.status_code}: {response.text}")
            return get_fallback_design(prompt)
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return get_fallback_design(prompt)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return get_fallback_design(prompt)

def get_fallback_design(prompt):
    """
    Fallback design when API fails
    """
    return {
        "building_type": f"AI-Generated Building ({prompt[:30]}...)",
        "floors": 3,
        "style": "Modern Contemporary",
        "features": ["Smart Design", "Energy Efficient", "Flexible Spaces"],
        "rooms": [
            {"name": "Main Lobby", "floor": 0, "type": "public", "width": 12.0, "depth": 8.0, "height": 5.0, "x": 0.0, "y": 0.0, "z": 0.0, "shape": "rectangle"},
            {"name": "Conference Room", "floor": 1, "type": "meeting", "width": 8.0, "depth": 6.0, "height": 3.5, "x": 0.0, "y": 0.0, "z": 4.0, "shape": "rectangle"},
            {"name": "Open Office", "floor": 1, "type": "workspace", "width": 15.0, "depth": 10.0, "height": 3.5, "x": 9.0, "y": 0.0, "z": 4.0, "shape": "rectangle"},
            {"name": "Executive Suite", "floor": 2, "type": "private", "width": 10.0, "depth": 8.0, "height": 3.5, "x": 0.0, "y": 0.0, "z": 8.0, "shape": "rectangle"},
            {"name": "Innovation Lab", "floor": 2, "type": "workspace", "width": 12.0, "depth": 8.0, "height": 4.0, "x": 11.0, "y": 0.0, "z": 8.0, "shape": "rectangle"}
        ],
        "structural_elements": [
            {"name": "Support Columns", "type": "column", "positions": [[0, 0], [10, 0], [20, 0], [0, 10], [10, 10], [20, 10]], "height": 12.0},
            {"name": "Glass Facade", "type": "facade", "curve_points": [[0, 0, 0], [10, 2, 0], [20, 0, 0]], "height": 12.0}
        ]
    }

# Test the API
if __name__ == "__main__":
    api_key = "AIzaSyChN9E0pmFhdhs6QyEtjJap-FW-JUsdAW0"
    test_prompt = "Design a modern sustainable office building with 3 floors"
    
    print("Testing Gemini API...")
    result = call_gemini_api(test_prompt, api_key)
    print(json.dumps(result, indent=2)) 