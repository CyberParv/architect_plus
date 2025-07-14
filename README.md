# Architect Plus

A Python-based web application for architectural space planning and design automation using Google's Gemini AI and Autodesk's Dynamo.

## Features

- Space planning automation
- Design optimization
- Integration with Google Gemini AI
- Integration with Autodesk Dynamo
- Web-based interface

## Prerequisites

- Python 3.8+
- Google Gemini API key
- Autodesk Dynamo (for space planning features)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/architect_plus.git
cd architect_plus
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Start the development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
architect_plus/
├── api/                    # API endpoints
├── static/                 # Static assets (CSS, JS)
├── templates/              # HTML templates
├── app.py                  # Main application entry point
├── design_automation.py    # Design automation integration
├── dynamo_integration.py   # Dynamo integration
├── gemini_integration.py   # Gemini AI integration
├── requirements.txt        # Python dependencies
└── sample_rooms.json      # Sample data
```

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 