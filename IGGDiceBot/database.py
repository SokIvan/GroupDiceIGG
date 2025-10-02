import os
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import SUPABASE_URL, SUPABASE_KEY

class Database:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
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
            response = self.client.table("users").insert(data).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    async def get_user(self, tg_id: int) -> Optional[Dict]:
        try:
            response = self.client.table("users").select("*").eq("tg_id", tg_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    async def update_user_status(self, tg_id: int, status: str) -> bool:
        try:
            data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("users").update(data).eq("tg_id", tg_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating user status: {e}")
            return False
    
    async def update_user_role(self, tg_id: int, role: str) -> bool:
        try:
            data = {
                "role": role,
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("users").update(data).eq("tg_id", tg_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating user role: {e}")
            return False
    
    async def update_user_name(self, tg_id: int, player_name: str) -> bool:
        try:
            data = {
                "player_name": player_name,
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("users").update(data).eq("tg_id", tg_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating user name: {e}")
            return False
    
    async def delete_user(self, tg_id: int) -> bool:
        try:
            response = self.client.table("users").delete().eq("tg_id", tg_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    async def get_all_users(self) -> List[Dict]:
        try:
            response = self.client.table("users").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    async def get_recent_name_changers(self) -> List[Dict]:
        """Получить пользователей, которые меняли имя за последние 24 часа"""
        try:
            time_24_hours_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
            response = self.client.table("users")\
                .select("*")\
                .gte("updated_at", time_24_hours_ago)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error getting recent name changers: {e}")
            return []
    
    async def get_leaders(self) -> List[Dict]:
        """Получить всех лидеров"""
        try:
            response = self.client.table("users").select("*").eq("role", "лидер").execute()
            return response.data
        except Exception as e:
            print(f"Error getting leaders: {e}")
            return []
    
    async def get_soldiers(self) -> List[Dict]:
        """Получить всех солдат"""
        try:
            response = self.client.table("users").select("*").eq("role", "солдат").execute()
            return response.data
        except Exception as e:
            print(f"Error getting soldiers: {e}")
            return []
    
    # Admins table operations
    async def is_admin(self, tg_id: int) -> bool:
        try:
            response = self.client.table("admins").select("*").eq("tg_id", tg_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error checking admin: {e}")
            return False
    
    async def add_admin(self, tg_id: int, username: str) -> bool:
        try:
            # Добавляем админа в таблицу админов
            admin_data = {"tg_id": tg_id, "username": username}
            response = self.client.table("admins").insert(admin_data).execute()
            
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
                self.client.table("users").insert(user_data).execute()
            
            return bool(response.data)
        except Exception as e:
            print(f"Error adding admin: {e}")
            return False
    
    # Fake names table operations
    async def add_fake_name(self, name: str) -> bool:
        try:
            data = {"name": name}
            response = self.client.table("fake_names").insert(data).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error adding fake name: {e}")
            return False
    
    async def delete_fake_name(self, name: str) -> bool:
        try:
            response = self.client.table("fake_names").delete().eq("name", name).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error deleting fake name: {e}")
            return False
    
    async def get_all_fake_names(self) -> List[Dict]:
        try:
            response = self.client.table("fake_names").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error getting fake names: {e}")
            return []