# 🚀 NeuraDoc Quick Start Guide

Get NeuraDoc running in 5 minutes!

## Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download AI Models (First Run Only)
```bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Start the Server
```bash
python start_server.py
```

### 4. Open Your Browser
Navigate to: `http://localhost:5000`

## 🎯 Test the Application

1. **Upload the test document**: Use `test_document.txt` (included in the project)
2. **Try "Ask Anything" mode**: Ask questions like:
   - "What are the three types of machine learning?"
   - "What challenges does AI face?"
   - "How is AI used in healthcare?"
3. **Try "Challenge Me" mode**: Generate logic-based questions about the document

## 🌟 Features to Explore

- **Document Upload**: Drag & drop PDF/TXT files
- **Smart Summarization**: AI-generated document summaries
- **Interactive Q&A**: Ask questions with grounded answers
- **Logic Challenges**: Test your understanding
- **Futuristic UI**: Dark theme with glassmorphism effects
- **Responsive Design**: Works on mobile and desktop

## 🔧 Troubleshooting

### Common Issues:

**"Module not found" errors:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**spaCy model issues:**
```bash
python -m spacy download en_core_web_sm
```

**Port already in use:**
```bash
# Kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Kill process on port 5000 (Mac/Linux)
lsof -ti:5000 | xargs kill -9
```

**Memory issues with large documents:**
- Try smaller documents first
- Ensure you have at least 4GB RAM available

## 📱 Browser Compatibility

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## 🎨 Customization

The application uses CSS variables for easy theming. Edit `frontend/style.css` to customize:
- Colors (see `:root` section)
- Animations
- Layout spacing
- Typography

## 🚀 Next Steps

- Upload your own documents
- Explore the challenge mode
- Customize the UI theme
- Check out the source code structure

---

**Need help?** Check the main README.md for detailed documentation! 