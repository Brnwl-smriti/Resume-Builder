# 🌌 NeuraDoc - AI-Powered Research Assistant

A **one-of-a-kind, dark-themed, full-stack AI-powered web application** that reads user-uploaded documents (PDF/TXT), understands their content deeply, and enables interactive question answering and logic-based challenges.

## ✨ Key Features

### 🎨 **Unique Dark-Themed UI/UX**
- Futuristic, elegant, and minimalist design
- Glassmorphism panels with ambient glow effects
- Smooth transitions and animated loaders
- Fully responsive (mobile + desktop)
- Custom-built UI (no Bootstrap/Streamlit defaults)

### 🧠 **Advanced AI Capabilities**
- **Document Upload & Parsing**: Support for PDF and TXT files
- **Auto Summarization**: Intelligent document summarization (≤150 words)
- **Ask Anything Mode**: Interactive Q&A with document-grounded answers
- **Challenge Me Mode**: Auto-generated logic-based questions with semantic evaluation
- **Zero Hallucination Policy**: All responses grounded in uploaded document

### 🔍 **Smart Features**
- **Justified Answers**: All responses include references with sentence highlighting
- **Semantic Search**: Advanced similarity search for relevant document chunks
- **Memory System**: Maintains conversation context
- **Typing Animation**: Realistic AI response simulation
- **Floating Assistant Avatar**: Interactive AI pulse orb

## 🏗️ Architecture

```
genai-assistant/
│
├── frontend/           # Custom-built dark-themed UI
│   ├── index.html     # Main application interface
│   ├── style.css      # Futuristic styling with CSS variables
│   └── script.js      # Interactive functionality
│
├── backend/           # Python Flask API
│   ├── app.py        # Main Flask application
│   ├── utils/        # AI processing modules
│   │   ├── summarizer.py    # Document summarization
│   │   ├── parser.py        # PDF/TXT parsing
│   │   ├── qa_engine.py     # Question-answering system
│   │   ├── challenge_gen.py # Challenge question generation
│   │   └── evaluator.py     # Answer evaluation
│
├── uploads/           # Temporary document storage
├── models/           # Optional: Saved AI models
├── requirements.txt  # Python dependencies
└── start_server.py   # Server startup script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd "Smart Assistant for Research Summarization"
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download required NLP models:**
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

4. **Start the server:**
   ```bash
   python start_server.py
   ```

5. **Open your browser:**
   Navigate to `http://localhost:5000`

## 🎯 How to Use

### 1. **Upload Document**
- Drag & drop or click to upload PDF/TXT files
- Automatic parsing and summarization
- Real-time progress indicators

### 2. **Ask Anything Mode**
- Ask questions about your document
- Get grounded answers with references
- View highlighted source sentences

### 3. **Challenge Me Mode**
- Generate logic-based questions
- Submit your answers
- Receive semantic evaluation and feedback

## 🔧 Technical Stack

### Frontend
- **HTML5/CSS3**: Custom dark-themed interface
- **Vanilla JavaScript**: Interactive functionality
- **Google Fonts**: Typography
- **CSS Variables**: Theme control

### Backend
- **Flask**: Web framework
- **Transformers**: AI models (BART, RoBERTa)
- **Sentence-Transformers**: Semantic embeddings
- **PyMuPDF**: PDF parsing
- **spaCy/NLTK**: Natural language processing
- **scikit-learn**: Similarity calculations

## 🌟 Unique Differentiators

| Feature | NeuraDoc | Generic Tools |
|---------|----------|---------------|
| **UI/UX** | Hand-crafted futuristic design | Bootstrap/Streamlit defaults |
| **AI Personality** | Typing animation, glowing avatar | Static responses |
| **Answer Quality** | Justified with references | Basic responses |
| **Challenge Mode** | Logic questions + semantic evaluation | Simple Q&A only |
| **Hallucination Prevention** | Document-grounded responses | May fabricate answers |
| **Visual Appeal** | Dark theme with glassmorphism | Standard light themes |

## 📸 Features in Action

- **Document Processing**: Intelligent parsing with progress tracking
- **Smart Summarization**: Context-aware document summaries
- **Interactive Q&A**: Real-time question answering with citations
- **Challenge Generation**: AI-powered logic questions
- **Answer Evaluation**: Semantic similarity-based feedback
- **Memory System**: Context-aware conversations

## 🔒 Privacy & Security

- Documents processed locally (no cloud uploads)
- Temporary storage with automatic cleanup
- No data persistence beyond session

## 🤝 Contributing

This is a showcase project demonstrating advanced AI integration with custom UI/UX design. Feel free to fork and extend with additional features!

## 📄 License

MIT License - Feel free to use and modify for your projects.

---

**Built with ❤️ for the AI research community** 