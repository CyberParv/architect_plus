# 🏗️ Architect Plus

**AI-Powered Architectural Design Generator**

A modern, dark-themed web application that uses Google's Gemini AI to generate architectural design specifications from natural language descriptions.

## ✨ Features

- **Modern Dark UI**: Sleek interface with neon blue/purple accents
- **AI-Powered Design**: Uses Google Gemini API for intelligent design generation
- **JSON Output**: Structured architectural specifications
- **Local File Storage**: Saves designs to `./output/design.json`
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Loading**: Shows progress while generating designs

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI**: Google Generative AI (Gemini)
- **Styling**: Custom CSS with modern dark theme
- **Environment**: Python-dotenv for secure API key management

## 📦 Installation

1. **Clone or download the project**
   ```bash
   cd architect_plus
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Google Gemini API key**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:5000`
   - Start generating architectural designs!

## 🚀 Usage

1. **Enter your design description** in the text area
   - Example: "A modern 2-story family home with 4 bedrooms, open-plan living area, and a double garage"

2. **Click "Generate Design"** to process your request

3. **View the results** in the JSON output section below

4. **Check the saved file** at `./output/design.json`

## 📋 Sample Output

```json
{
  "length": 20.0,
  "width": 15.0,
  "height": 3.5,
  "wall_thickness": 0.25,
  "rooms": 4,
  "floors": 2,
  "foundation_type": "concrete slab",
  "roof_type": "gable",
  "material": "brick",
  "estimated_cost": 250000,
  "construction_time": "8-10 months"
}
```

## 🎨 Customization

### Modifying the UI
- Edit `static/styles.css` to change colors, fonts, or layout
- Update `templates/index.html` to modify the structure

### Changing the AI Prompt
- Edit the `prompt` variable in `app.py` to customize how Gemini generates designs
- Modify the JSON structure in the prompt to add/remove fields

### Adding New Features
- Add new routes in `app.py` for additional functionality
- Extend the JavaScript in `index.html` for new UI interactions

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable/disable debug mode

### File Structure
```
architect_plus/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   └── styles.css        # CSS styling
└── output/
    └── design.json       # Generated designs
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'google.generativeai'"**
   - Run: `pip install -r requirements.txt`

2. **"API key not found"**
   - Make sure your `.env` file exists and contains `GEMINI_API_KEY=your_key_here`

3. **"Failed to connect to the server"**
   - Ensure Flask is running on `localhost:5000`
   - Check your internet connection for API calls

4. **JSON parsing errors**
   - The app includes fallback JSON structure if Gemini returns invalid JSON

## 🌟 Future Enhancements

- Add 3D visualization of generated designs
- Support for architectural drawing generation
- Multiple design style options
- Export to CAD formats
- User authentication and design history
- Advanced material and cost calculations

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

---

**Built with ❤️ using Flask and Google Gemini AI** 