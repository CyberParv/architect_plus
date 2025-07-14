# 🏗️ Architect Plus

**AI-Powered Architectural Design Generator**

A modern Flask web application that uses Google's Gemini AI to generate detailed architectural design specifications from natural language descriptions.

## ✨ Features

- **AI-Powered Design**: Uses Google Gemini API for intelligent architectural design generation
- **Modern Dark UI**: Sleek interface with neon blue/purple accents
- **JSON Output**: Structured architectural specifications including rooms, walls, and structural elements
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Generation**: Shows progress while generating designs

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI**: Google Generative AI (Gemini)
- **Styling**: Custom CSS with modern dark theme

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/architect-plus.git
   cd architect-plus
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows (PowerShell)
   venv\Scripts\Activate.ps1
   
   # On Windows (Command Prompt)
   venv\Scripts\activate.bat
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   **Option A: Using environment variables (Recommended)**
   ```bash
   # On Windows (PowerShell)
   $env:GEMINI_API_KEY="your_actual_api_key_here"
   
   # On Windows (Command Prompt)
   set GEMINI_API_KEY=your_actual_api_key_here
   
   # On macOS/Linux
   export GEMINI_API_KEY="your_actual_api_key_here"
   ```
   
   **Option B: Using .env file**
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🚀 Usage

1. **Enter your design description** in the text area
   - Example: "A modern 2-story family home with 4 bedrooms, open-plan living area, and a double garage"

2. **Click "Generate Design"** to process your request

3. **View the results** in the JSON output section

4. **Copy or save** the generated architectural specifications

## 📋 Sample Output

```json
{
  "project": {
    "name": "Modern Family Home",
    "style": "contemporary",
    "floors": 2,
    "site": {"width": 20.0, "depth": 15.0}
  },
  "rooms": [
    {
      "name": "Living Room",
      "floor": 1,
      "width": 8.0,
      "depth": 6.0,
      "height": 3.5,
      "position": {"x": 0, "y": 0, "z": 0},
      "shape": "rectangle",
      "features": ["fireplace", "large_windows"]
    }
  ],
  "walls": [...],
  "structural": [...],
  "exterior": {...}
}
```

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable/disable debug mode

### Customization

- **UI Styling**: Edit `static/styles.css` to modify colors, fonts, or layout
- **HTML Structure**: Update `templates/index.html` to change the interface
- **AI Prompts**: Modify the prompt in `app.py` to customize AI behavior

## 🐛 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not set" error**
   - Make sure you've set the environment variable correctly
   - Verify your API key is valid and has sufficient quota

2. **"Module not found" errors**
   - Ensure you've activated the virtual environment
   - Run `pip install -r requirements.txt` to install dependencies

3. **PowerShell execution policy errors**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Port already in use**
   - Change the port in `app.py`: `app.run(port=5001)`
   - Or kill the process using the port

### Getting Help

- Check the [Issues](https://github.com/yourusername/architect-plus/issues) page
- Create a new issue with detailed error information
- Include your Python version and operating system

## 🌟 Future Enhancements

- 3D visualization of generated designs
- Export to CAD formats
- Multiple architectural styles
- User authentication and design history
- Advanced material and cost calculations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Google Gemini AI for powerful language generation
- Flask community for the excellent web framework
- Contributors and users who help improve this project

---

**Built with ❤️ using Flask and Google Gemini AI**