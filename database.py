
from datetime import datetime
from typing import List, Dict, Optional
from supabase_client import supabase


class BillDatabase:
    def __init__(self):
        self.table = "expenditures"
    
    def add_expenditure(self, item: str, quantity: str, date, amount: float, category: str, person: str) -> int:
        # Handle date conversion to string if it's a date object
        if hasattr(date, 'strftime'):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = str(date)
        data = {
            "item": item,
            "quantity": quantity,
            "date": date_str,
            "amount": amount,
            "category": category,
            "person": person
        }
        res = supabase.table(self.table).insert(data).execute()
        if res.data and len(res.data) > 0:
            return res.data[0].get("id", -1)
        return -1
    
    def get_all_expenditures(self) -> List[Dict]:
        res = supabase.table(self.table).select("*").order("date", desc=True).order("created_at", desc=True).execute()
        return res.data if res.data else []
    
    def get_expenditures_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        res = supabase.table(self.table).select("*").gte("date", start_date).lte("date", end_date).order("date", desc=True).order("created_at", desc=True).execute()
        return res.data if res.data else []
    
    def delete_expenditure(self, expenditure_id: int) -> bool:
        res = supabase.table(self.table).delete().eq("id", expenditure_id).execute()
        return bool(res.data)
    
    def get_total_by_category(self, category: str = None) -> float:
        if category:
            res = supabase.table(self.table).select("amount").eq("category", category).execute()
        else:
            res = supabase.table(self.table).select("amount").execute()
        total = sum(row["amount"] for row in res.data) if res.data else 0.0
        return total
    
    def update_expenditure(self, expenditure_id: int, item: str, quantity: str, date, amount: float, category: str, person: str) -> bool:
        if hasattr(date, 'strftime'):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = str(date)
        data = {
            "item": item,
            "quantity": quantity,
            "date": date_str,
            "amount": amount,
            "category": category,
            "person": person
        }
        res = supabase.table(self.table).update(data).eq("id", expenditure_id).execute()
        return bool(res.data)
