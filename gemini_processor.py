import google.generativeai as genai
from PIL import Image
import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Optional
import base64
from datetime import datetime

# Load environment variables
load_dotenv()

class GeminiProcessor:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
    
    def process_bill_image(self, image_path: str) -> List[Dict]:
        """
        Process a bill image using Gemini and extract structured data.
        
        Args:
            image_path: Path to the bill image
            
        Returns:
            List of dictionaries containing extracted bill items
        """
        try:
            # Open and process the image
            image = Image.open(image_path)
            
            # Create a detailed prompt for bill processing
            prompt = """
            Analyze this bill/receipt image and extract all the items with their details.
            
            Please return the data in the following JSON format:
            {
                "items": [
                    {
                        "item": "item name",
                        "quantity": "quantity with unit (e.g., 1 kg, 2 pieces, 500ml)",
                        "amount": 150.00,
                        "category": "category (e.g., Groceries, Snacks, Beverages, etc.)"
                    }
                ],
                "total_amount": 450.00,
                "date": "YYYY-MM-DD",
                "store_name": "store name if visible"
            }
            
            Rules:
            1. Extract each line item separately
            2. For quantity, include the unit (kg, grams, pieces, liters, etc.)
            3. For amount, use only the numeric value (no currency symbols)
            4. For category, choose from: Groceries, Snacks, Beverages, Personal Care, Household, Medicine, or Other
            5. If date is not clear, use today's date
            6. If quantity is not specified, use "1 piece"
            7. Return only valid JSON, no additional text
            """
            
            # Generate content using Gemini
            response = self.model.generate_content([prompt, image])
            
            # Parse the response
            response_text = response.text.strip()
            
            # Clean up the response text to extract JSON
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            # Parse JSON response
            try:
                bill_data = json.loads(response_text)
                
                # Add current date if not provided
                if 'date' not in bill_data or not bill_data['date']:
                    bill_data['date'] = datetime.now().strftime('%Y-%m-%d')
                
                return bill_data
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Raw response: {response_text}")
                return {"items": [], "total_amount": 0, "date": datetime.now().strftime('%Y-%m-%d')}
                
        except Exception as e:
            print(f"Error processing image: {e}")
            return {"items": [], "total_amount": 0, "date": datetime.now().strftime('%Y-%m-%d')}
    
    def process_multiple_images(self, image_paths: List[str]) -> List[Dict]:
        """
        Process multiple bill images.
        
        Args:
            image_paths: List of paths to bill images
            
        Returns:
            List of processed bill data
        """
        results = []
        for image_path in image_paths:
            result = self.process_bill_image(image_path)
            results.append(result)
        
        return results
    
    def validate_extracted_data(self, bill_data: Dict) -> bool:
        """
        Validate the extracted bill data.
        
        Args:
            bill_data: Dictionary containing bill data
            
        Returns:
            True if data is valid, False otherwise
        """
        required_fields = ['items', 'total_amount', 'date']
        
        for field in required_fields:
            if field not in bill_data:
                return False
        
        if not isinstance(bill_data['items'], list):
            return False
        
        for item in bill_data['items']:
            required_item_fields = ['item', 'quantity', 'amount', 'category']
            for field in required_item_fields:
                if field not in item:
                    return False
        
        return True
