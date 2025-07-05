import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class BillDatabase:
    def __init__(self, db_path: str = "bills.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the required table structure."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenditures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                quantity TEXT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT,
                person TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_expenditure(self, item: str, quantity: str, date, amount: float, 
                       category: str, person: str) -> int:
        """Add a new expenditure to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Handle date conversion to string if it's a date object
        if hasattr(date, 'strftime'):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = str(date)
        
        cursor.execute('''
            INSERT INTO expenditures (item, quantity, date, amount, category, person)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (item, quantity, date_str, amount, category, person))
        
        expenditure_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return expenditure_id
    
    def get_all_expenditures(self) -> List[Dict]:
        """Get all expenditures from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, item, quantity, date, amount, category, person, created_at
            FROM expenditures
            ORDER BY date DESC, created_at DESC
        ''')
        
        columns = [description[0] for description in cursor.description]
        expenditures = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return expenditures
    
    def get_expenditures_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get expenditures within a date range."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, item, quantity, date, amount, category, person, created_at
            FROM expenditures
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC, created_at DESC
        ''', (start_date, end_date))
        
        columns = [description[0] for description in cursor.description]
        expenditures = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return expenditures
    
    def delete_expenditure(self, expenditure_id: int) -> bool:
        """Delete an expenditure by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM expenditures WHERE id = ?', (expenditure_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_total_by_category(self, category: str = None) -> float:
        """Get total amount by category or overall total."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('SELECT SUM(amount) FROM expenditures WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT SUM(amount) FROM expenditures')
        
        total = cursor.fetchone()[0] or 0.0
        conn.close()
        
        return total
    
    def update_expenditure(self, expenditure_id: int, item: str, quantity: str, 
                          date, amount: float, category: str, person: str) -> bool:
        """Update an existing expenditure."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Handle date conversion to string if it's a date object
        if hasattr(date, 'strftime'):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = str(date)
        
        cursor.execute('''
            UPDATE expenditures 
            SET item = ?, quantity = ?, date = ?, amount = ?, category = ?, person = ?
            WHERE id = ?
        ''', (item, quantity, date_str, amount, category, person, expenditure_id))
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
