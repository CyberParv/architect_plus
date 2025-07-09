# Architect Plus - Vercel Deployment

## 🚀 Deploy to Vercel

This is a simplified version of Architect Plus optimized for Vercel deployment.

### Features
- ✅ AI-Powered Architectural Design Generation
- ✅ Google Gemini Integration
- ✅ Modern Dark UI
- ✅ JSON Export
- ❌ Professional Spaceplanning (not available in serverless environment)

### Quick Deploy

1. **Fork this repository**
2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Configure environment variables

3. **Set Environment Variables**:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Deploy**:
   - Vercel will automatically build and deploy
   - Your app will be available at `https://your-project.vercel.app`

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GEMINI_API_KEY=your_api_key_here

# Run locally
python api/index.py
```

### File Structure
```
├── api/
│   └── index.py          # Main Flask application
├── templates/
│   └── index.html        # HTML template
├── static/
│   └── styles.css        # CSS styles
├── vercel.json           # Vercel configuration
└── requirements.txt      # Python dependencies
```

### API Endpoints
- `GET /` - Main web interface
- `POST /generate-design` - Generate architectural design
- `GET /health` - Health check
- `GET /spaceplanning-info` - Spaceplanning availability (returns false for Vercel)

### Limitations in Vercel Deployment
- No file system persistence
- No professional spaceplanning integration
- Serverless function timeout limits
- No Dynamo script execution

### Usage
1. Visit your deployed URL
2. Enter architectural description
3. Click "Generate Design"
4. View JSON architectural specifications

Built with Flask + Google Gemini AI 