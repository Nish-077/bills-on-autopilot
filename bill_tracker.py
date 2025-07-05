import cv2
import os
from datetime import datetime
import argparse
from typing import List, Optional
from database import BillDatabase
from gemini_processor import GeminiProcessor

class BillTracker:
    def __init__(self):
        self.db = BillDatabase()
        self.gemini = GeminiProcessor()
        self.camera = None
    
    def capture_photo(self, save_path: str = None) -> str:
        """
        Capture a photo using the camera.
        
        Args:
            save_path: Path to save the captured image
            
        Returns:
            Path to the saved image
        """
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            raise Exception("Cannot open camera")
        
        print("Press SPACE to capture photo, ESC to exit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Display the frame
            cv2.imshow('Bill Tracker - Press SPACE to capture', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 32:  # SPACE key
                # Generate filename if not provided
                if save_path is None:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    save_path = f"bill_{timestamp}.jpg"
                
                # Save the image
                cv2.imwrite(save_path, frame)
                print(f"Photo saved: {save_path}")
                break
            
            elif key == 27:  # ESC key
                print("Capture cancelled")
                cap.release()
                cv2.destroyAllWindows()
                return None
        
        cap.release()
        cv2.destroyAllWindows()
        return save_path
    
    def process_and_store_bill(self, image_path: str, person: str = "Unknown") -> bool:
        """
        Process a bill image and store the extracted data.
        
        Args:
            image_path: Path to the bill image
            person: Person who made the purchase
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Processing bill image: {image_path}")
            
            # Process the image with Gemini
            bill_data = self.gemini.process_bill_image(image_path)
            
            if not bill_data or not bill_data.get('items'):
                print("No items found in the bill")
                return False
            
            print(f"Found {len(bill_data['items'])} items")
            
            # Store each item in the database
            for item_data in bill_data['items']:
                expenditure_id = self.db.add_expenditure(
                    item=item_data['item'],
                    quantity=item_data['quantity'],
                    date=bill_data['date'],
                    amount=item_data['amount'],
                    category=item_data['category'],
                    person=person
                )
                
                print(f"Added: {item_data['item']} - ₹{item_data['amount']}")
            
            print(f"Successfully processed bill. Total: ₹{bill_data['total_amount']}")
            return True
            
        except Exception as e:
            print(f"Error processing bill: {e}")
            return False
    
    def capture_and_process(self, person: str = "Unknown") -> bool:
        """
        Capture a photo and process it in one step.
        
        Args:
            person: Person who made the purchase
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Capture photo
            image_path = self.capture_photo()
            
            if image_path is None:
                return False
            
            # Process and store
            success = self.process_and_store_bill(image_path, person)
            
            # Optionally delete the temporary image
            if os.path.exists(image_path):
                os.remove(image_path)
            
            return success
            
        except Exception as e:
            print(f"Error in capture and process: {e}")
            return False
    
    def process_existing_images(self, image_paths: List[str], person: str = "Unknown") -> int:
        """
        Process multiple existing images.
        
        Args:
            image_paths: List of image paths
            person: Person who made the purchases
            
        Returns:
            Number of successfully processed images
        """
        success_count = 0
        
        for image_path in image_paths:
            if not os.path.exists(image_path):
                print(f"Image not found: {image_path}")
                continue
            
            if self.process_and_store_bill(image_path, person):
                success_count += 1
        
        return success_count
    
    def show_recent_expenditures(self, count: int = 10):
        """
        Show recent expenditures.
        
        Args:
            count: Number of recent expenditures to show
        """
        expenditures = self.db.get_all_expenditures()
        
        if not expenditures:
            print("No expenditures found")
            return
        
        print(f"\n--- Recent {min(count, len(expenditures))} Expenditures ---")
        print(f"{'Item':<20} {'Quantity':<10} {'Date':<12} {'Amount':<10} {'Category':<12} {'Person':<10}")
        print("-" * 80)
        
        for exp in expenditures[:count]:
            print(f"{exp['item']:<20} {exp['quantity']:<10} {exp['date']:<12} "
                  f"₹{exp['amount']:<9.2f} {exp['category']:<12} {exp['person']:<10}")
        
        total = sum(exp['amount'] for exp in expenditures[:count])
        print(f"\nTotal for shown items: ₹{total:.2f}")

def main():
    parser = argparse.ArgumentParser(description='Bill Tracker - Extract items from bill photos')
    parser.add_argument('--capture', action='store_true', help='Capture a new photo')
    parser.add_argument('--process', nargs='+', help='Process existing image files')
    parser.add_argument('--person', default='Unknown', help='Person who made the purchase')
    parser.add_argument('--show', type=int, default=10, help='Show recent expenditures')
    
    args = parser.parse_args()
    
    tracker = BillTracker()
    
    if args.capture:
        print("Starting camera capture...")
        success = tracker.capture_and_process(args.person)
        if success:
            print("✅ Bill processed successfully!")
        else:
            print("❌ Failed to process bill")
    
    elif args.process:
        print(f"Processing {len(args.process)} image(s)...")
        success_count = tracker.process_existing_images(args.process, args.person)
        print(f"✅ Successfully processed {success_count}/{len(args.process)} images")
    
    # Always show recent expenditures
    tracker.show_recent_expenditures(args.show)

if __name__ == "__main__":
    main()
