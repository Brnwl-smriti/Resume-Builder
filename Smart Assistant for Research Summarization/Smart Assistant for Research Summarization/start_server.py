#!/usr/bin/env python3
"""
NeuraDoc Server Startup Script
Initializes the Flask application and handles dependencies
"""

import os
import sys
import subprocess
import importlib.util

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'transformers', 'sentence_transformers', 'PyMuPDF',
        'sumy', 'scikit-learn', 'spacy', 'nltk', 'numpy', 'torch'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run:")
            print("   pip install -r requirements.txt")
            return False
    
    return True

def download_nlp_models():
    """Download required NLP models"""
    print("🤖 Downloading NLP models...")
    
    # Download spaCy model
    try:
        import spacy
        try:
            spacy.load('en_core_web_sm')
            print("✅ spaCy model already available")
        except OSError:
            print("📥 Downloading spaCy model...")
            subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
            print("✅ spaCy model downloaded")
    except Exception as e:
        print(f"⚠️  spaCy model download failed: {e}")
    
    # Download NLTK data
    try:
        import nltk
        nltk_data = ['punkt', 'punkt_tab', 'stopwords']
        for data in nltk_data:
            try:
                if data == 'punkt' or data == 'punkt_tab':
                    nltk.data.find(f'tokenizers/{data}')
                else:
                    nltk.data.find(f'corpora/{data}')
                print(f"✅ NLTK {data} already available")
            except LookupError:
                print(f"📥 Downloading NLTK {data}...")
                nltk.download(data)
                print(f"✅ NLTK {data} downloaded")
    except Exception as e:
        print(f"⚠️  NLTK data download failed: {e}")

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'models', 'frontend']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def main():
    """Main startup function"""
    print("🌌 NeuraDoc AI Assistant - Starting up...")
    print("=" * 50)
    
    # Check and install dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Download NLP models
    download_nlp_models()
    
    # Create directories
    create_directories()
    
    print("\n🚀 Starting NeuraDoc server...")
    print("📱 Open your browser and navigate to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the Flask application
    try:
        import sys
        import os
        # Add the current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from backend.app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 NeuraDoc server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 