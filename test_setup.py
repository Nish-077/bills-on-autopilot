#!/usr/bin/env python3
"""
Test script to verify the Bill Tracker setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import sqlite3
        print("✅ sqlite3 imported successfully")
        
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import cv2
        print("✅ opencv-python imported successfully")
        
        from PIL import Image
        print("✅ pillow imported successfully")
        
        import streamlit as st
        print("✅ streamlit imported successfully")
        
        import plotly.express as px
        print("✅ plotly imported successfully")
        
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
        
        try:
            import google.generativeai as genai
            print("✅ google-generativeai imported successfully")
        except ImportError as e:
            print(f"❌ google-generativeai import failed: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    try:
        print("\nTesting database...")
        from database import BillDatabase
        
        # Create a test database
        db = BillDatabase("test_bills.db")
        
        # Test adding an expenditure
        expenditure_id = db.add_expenditure(
            item="Test Item",
            quantity="1 piece",
            date="2025-01-01",
            amount=100.0,
            category="Test",
            person="TestUser"
        )
        
        print(f"✅ Database test passed - Added expenditure with ID: {expenditure_id}")
        
        # Clean up test database
        os.remove("test_bills.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_env_file():
    """Test .env file configuration"""
    try:
        print("\nTesting .env configuration...")
        
        if not os.path.exists(".env"):
            print("❌ .env file not found")
            return False
        
        # Read .env file directly to avoid system env conflicts
        env_content = {}
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_content[key.strip()] = value.strip()
        
        api_key = env_content.get('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in .env file")
            print("   Please add your Gemini API key to .env file")
            return False
        
        if api_key == "your_gemini_api_key_here":
            print("❌ GOOGLE_API_KEY is still set to placeholder value")
            print("   Please add your actual Gemini API key to .env file")
            return False
        
        # Also check if it's a valid-looking API key
        if not api_key.startswith("AIzaSy") or len(api_key) < 30:
            print("❌ GOOGLE_API_KEY doesn't look like a valid Gemini API key")
            print("   Gemini API keys typically start with 'AIzaSy' and are longer")
            return False
        
        print("✅ .env file configured correctly")
        print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
        return True
        
    except Exception as e:
        print(f"❌ .env test failed: {e}")
        return False

def test_gemini_processor():
    """Test Gemini processor initialization"""
    try:
        print("\nTesting Gemini processor...")
        
        # Read .env file directly to get the actual API key
        env_content = {}
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_content[key.strip()] = value.strip()
        
        api_key = env_content.get('GOOGLE_API_KEY')
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️  Skipping Gemini test - API key not configured")
            return True
        
        # Temporarily set the environment variable for this test
        original_key = os.environ.get('GOOGLE_API_KEY')
        os.environ['GOOGLE_API_KEY'] = api_key
        
        try:
            from gemini_processor import GeminiProcessor
            processor = GeminiProcessor()
            print("✅ Gemini processor initialized successfully")
            print(f"   Using API key: {api_key[:10]}...{api_key[-4:]}")
            return True
        finally:
            # Restore original environment variable
            if original_key:
                os.environ['GOOGLE_API_KEY'] = original_key
            else:
                os.environ.pop('GOOGLE_API_KEY', None)
        
    except Exception as e:
        print(f"❌ Gemini processor test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Bill Tracker setup tests...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Database Test", test_database),
        ("Environment Test", test_env_file),
        ("Gemini Test", test_gemini_processor)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Running {test_name}")
        print(f"{'='*50}")
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
        
        print()
    
    print(f"{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 All tests passed! Your Bill Tracker is ready to use!")
        print("\nNext steps:")
        print("1. Make sure your .env file has your Gemini API key")
        print("2. Run the web interface: streamlit run streamlit_app.py")
        print("3. Or use the CLI: python bill_tracker.py --help")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
