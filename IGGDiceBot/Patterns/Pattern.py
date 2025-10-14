# Pattern.py - небольшие улучшения

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import json

@dataclass
class Pattern:
    id: int
    pattern_name: str
    pattern_elements: List[str]
    pattern_mas_elements: List[List[str]]
    status: str
    created_at: datetime
    
    @classmethod
    def from_db(cls, data: Dict[str, Any]):
        # Безопасная загрузка JSON
        pattern_mas_elements = []
        try:
            pattern_mas_elements = json.loads(data['pattern_mas_elements'])
        except (json.JSONDecodeError, KeyError):
            pattern_mas_elements = []
        
        # Безопасное разделение строки
        pattern_elements = []
        try:
            pattern_elements = data['pattern_elements'].split(',')
        except (AttributeError, KeyError):
            pattern_elements = []
        
        return cls(
            id=data['id'],
            pattern_name=data['pattern_name'],
            pattern_elements=pattern_elements,
            pattern_mas_elements=pattern_mas_elements,
            status=data['status'],
            created_at=data['created_at']
        )