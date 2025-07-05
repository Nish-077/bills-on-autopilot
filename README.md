# Bills on Autopilot 📄

An AI-powered bill tracking web app that automatically extracts items from bill photos using Google's Gemini AI. Upload your bills, let AI do the work, and track your expenses with beautiful analytics!

## Features

- 📸 **Smart Photo Processing**: Upload multiple bill images at once
- 🤖 **AI-Powered Extraction**: Uses Google Gemini to extract item details automatically
- 💾 **Expense Management**: Add, edit, delete, and search through your expenses
- 📊 **Beautiful Analytics**: View spending patterns, category breakdowns, and trends
- 🌐 **Modern Web Interface**: Clean, responsive Streamlit interface

## Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```
The setup script will:
- Install all dependencies
- Create a template `.env` file
- Guide you through the setup process

### Option 2: Manual Setup

### 1. Get Your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 2. Setup
```bash
pip install -r requirements.txt
```

Create a `.env` file with your API key:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run the App
```bash
streamlit run streamlit_app.py
```

## How to Use

1. **Process Bills**: Upload bill images and let AI extract the items
2. **View Expenses**: Browse, search, and edit your expenses
3. **Analytics**: See spending patterns and category breakdowns

## Deployment

See `DEPLOYMENT.md` for step-by-step instructions to deploy on Streamlit Community Cloud for free.

## Tips for Better Results

- Use clear, well-lit photos
- Ensure text is readable
- Place bills on flat surfaces
- Avoid shadows over the text
