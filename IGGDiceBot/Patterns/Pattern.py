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
        return cls(
            id=data['id'],
            pattern_name=data['pattern_name'],
            pattern_elements=data['pattern_elements'].split(','),
            pattern_mas_elements=json.loads(data['pattern_mas_elements']),
            status=data['status'],
            created_at=data['created_at']
        )