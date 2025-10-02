import requests
import json
from config import SUPABASE_URL, SUPABASE_KEY
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: dict = None):
        """Универсальный метод для выполнения запросов к Supabase"""
        url = f"{self.url}/{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    # Users table operations
    async def add_user(self, tg_id: int, username: str, tag: str, status: str = "pending") -> bool:
        try:
            data = {
                "tg_id": tg_id,
                "username": username,
                "tag": tag,
                "status": status,
                "player_name": "П У С Т О",
                "role": "участник",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            result = self._make_request("POST", "rest/v1/users", data)
            return result is not None
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    async def get_user(self, tg_id: int) -> Optional[Dict]:
        try:
            result = self._make_request("GET", f"rest/v1/users?tg_id=eq.{tg_id}")
            return result[0] if result and len(result) > 0 else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    async def update_user_status(self, tg_id: int, status: str) -> bool:
        try:
            data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            result = self._make_request("PATCH", f"rest/v1/users?tg_id=eq.{tg_id}", data)
            return result is not None
        except Exception as e:
            print(f"Error updating user status: {e}")
            return False
    
    async def update_user_role(self, tg_id: int, role: str) -> bool:
        try:
            data = {
                "role": role,
                "updated_at": datetime.utcnow().isoformat()
            }
            result = self._make_request("PATCH", f"rest/v1/users?tg_id=eq.{tg_id}", data)
            return result is not None
        except Exception as e:
            print(f"Error updating user role: {e}")
            return False
    
    async def update_user_name(self, tg_id: int, player_name: str) -> bool:
        try:
            data = {
                "player_name": player_name,
                "updated_at": datetime.utcnow().isoformat()
            }
            result = self._make_request("PATCH", f"rest/v1/users?tg_id=eq.{tg_id}", data)
            return result is not None
        except Exception as e:
            print(f"Error updating user name: {e}")
            return False
    
    async def delete_user(self, tg_id: int) -> bool:
        try:
            result = self._make_request("DELETE", f"rest/v1/users?tg_id=eq.{tg_id}")
            return result is not None
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    async def get_all_users(self) -> List[Dict]:
        try:
            result = self._make_request("GET", "rest/v1/users?select=*")
            return result if result else []
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    async def get_recent_name_changers(self) -> List[Dict]:
        """Получить пользователей, которые меняли имя за последние 24 часа"""
        try:
            time_24_hours_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
            result = self._make_request(
                "GET", 
                f"rest/v1/users?updated_at=gte.{time_24_hours_ago}&select=*"
            )
            return result if result else []
        except Exception as e:
            print(f"Error getting recent name changers: {e}")
            return []
    
    async def get_leaders(self) -> List[Dict]:
        """Получить всех лидеров"""
        try:
            result = self._make_request("GET", "rest/v1/users?role=eq.лидер&select=*")
            return result if result else []
        except Exception as e:
            print(f"Error getting leaders: {e}")
            return []
    
    async def get_soldiers(self) -> List[Dict]:
        """Получить всех солдат"""
        try:
            result = self._make_request("GET", "rest/v1/users?role=eq.солдат&select=*")
            return result if result else []
        except Exception as e:
            print(f"Error getting soldiers: {e}")
            return []
    
    # Admins table operations
    async def is_admin(self, tg_id: int) -> bool:
        try:
            result = self._make_request("GET", f"rest/v1/admins?tg_id=eq.{tg_id}")
            return len(result) > 0 if result else False
        except Exception as e:
            print(f"Error checking admin: {e}")
            return False
    
    async def add_admin(self, tg_id: int, username: str) -> bool:
        try:
            # Добавляем админа в таблицу админов
            admin_data = {"tg_id": tg_id, "username": username}
            result = self._make_request("POST", "rest/v1/admins", admin_data)
            
            # Также убедимся, что админ есть в таблице пользователей
            user_exists = await self.get_user(tg_id)
            if not user_exists:
                user_data = {
                    "tg_id": tg_id,
                    "username": username,
                    "tag": f"@{username}" if username else f"id{tg_id}",
                    "status": "approved",
                    "player_name": "П У С Т О",
                    "role": "участник",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                self._make_request("POST", "rest/v1/users", user_data)
            
            return result is not None
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False
    
    # Fake names table operations
    async def add_fake_name(self, name: str) -> bool:
        try:
            data = {"name": name}
            result = self._make_request("POST", "rest/v1/fake_names", data)
            return result is not None
        except Exception as e:
            print(f"Error adding fake name: {e}")
            return False
    
    async def delete_fake_name(self, name: str) -> bool:
        try:
            result = self._make_request("DELETE", f"rest/v1/fake_names?name=eq.{name}")
            return result is not None
        except Exception as e:
            print(f"Error deleting fake name: {e}")
            return False
    
    async def get_all_fake_names(self) -> List[Dict]:
        try:
            result = self._make_request("GET", "rest/v1/fake_names?select=*")
            return result if result else []
        except Exception as e:
            print(f"Error getting fake names: {e}")
            return []