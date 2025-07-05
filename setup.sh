#!/bin/bash

# Ghar Ke Bills Tracker Setup Script

echo "🚀 Setting up Ghar Ke Bills Tracker..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here
EOF
    echo "📝 Please edit .env file and add your Gemini API key"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
else
    echo "✅ .env file already exists"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Gemini API key"
echo "2. Run the app: streamlit run streamlit_app.py"
echo "3. Open your browser and start tracking bills!"
echo ""
echo "📖 See README.md for more details"
