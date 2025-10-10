import os
import string
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import SUPABASE_URL, SUPABASE_KEY

class Database:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Users table operations (остаются без изменений)
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

    async def get_user_by_player_name(self, player_name: string) -> Optional[Dict]:
        try:
            response = self.client.table("users").select("*").eq("player_name", player_name).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

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

    # Fake names table operations
    async def add_fake_name(self, player_name: str, role: str = "участник") -> bool:
        try:
            data = {
                "username": "Фиктивный игрок",
                "tag": "без Telegram",
                "status": "approved", 
                "player_name": player_name,
                "role": role,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("fake_names").insert(data).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error adding fake name: {e}")
            return False

    async def update_fake_name_role(self, fake_name_id: int, role: str) -> bool:
        try:
            data = {
                "role": role,
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("fake_names").update(data).eq("id", fake_name_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating fake name role: {e}")
            return False

    async def update_fake_name(self, fake_name_id: int, player_name: str) -> bool:
        try:
            data = {
                "player_name": player_name,
                "updated_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("fake_names").update(data).eq("id", fake_name_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error updating fake name: {e}")
            return False

    async def delete_fake_name(self, fake_name_id: int) -> bool:
        try:
            response = self.client.table("fake_names").delete().eq("id", fake_name_id).execute()
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

    # Allowed chats operations
    async def add_allowed_chat(self, chat_id: int, chat_title: str = "") -> bool:
        try:
            data = {
                "chat_id": chat_id,
                "chat_title": chat_title,
                "created_at": datetime.utcnow().isoformat()
            }
            response = self.client.table("allowed_chats").insert(data).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error adding allowed chat: {e}")
            return False

    async def remove_allowed_chat(self, chat_id: int) -> bool:
        try:
            response = self.client.table("allowed_chats").delete().eq("chat_id", chat_id).execute()
            return bool(response.data)
        except Exception as e:
            print(f"Error removing allowed chat: {e}")
            return False

    async def is_chat_allowed(self, chat_id: int) -> bool:
        try:
            response = self.client.table("allowed_chats").select("*").eq("chat_id", chat_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Error checking allowed chat: {e}")
            return False

    async def get_all_allowed_chats(self) -> List[Dict]:
        try:
            response = self.client.table("allowed_chats").select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error getting allowed chats: {e}")
            return []

    # Комбинированные методы для работы со всеми игроками (остаются без изменений)
    async def get_all_players(self) -> List[Dict]:
        """Получить всех игроков (реальные + фиктивные)"""
        try:
            users = await self.get_all_users()
            fake_names = await self.get_all_fake_names()
            
            for user in users:
                user['player_type'] = 'telegram'
            for fake in fake_names:
                fake['player_type'] = 'fake'
            
            all_players = users + fake_names
            return sorted(all_players, key=lambda x: x['player_name'])
        except Exception as e:
            print(f"Error getting all players: {e}")
            return []

    async def get_recent_players(self) -> List[Dict]:
        """Получить игроков, которые менялись/создавались за последние 24 часа"""
        try:
            time_24_hours_ago = (datetime.utcnow() - timedelta(hours=24)).isoformat()
            
            recent_users = self.client.table("users")\
                .select("*")\
                .gte("updated_at", time_24_hours_ago)\
                .execute().data
            
            recent_fakes = self.client.table("fake_names")\
                .select("*")\
                .gte("updated_at", time_24_hours_ago)\
                .execute().data
            
            for user in recent_users:
                user['player_type'] = 'telegram'
            for fake in recent_fakes:
                fake['player_type'] = 'fake'
            
            return recent_users + recent_fakes
        except Exception as e:
            print(f"Error getting recent players: {e}")
            return []

    async def get_leaders(self) -> List[Dict]:
        """Получить всех лидеров (реальные + фиктивные)"""
        try:
            user_leaders = self.client.table("users")\
                .select("*")\
                .eq("role", "лидер")\
                .execute().data
            
            fake_leaders = self.client.table("fake_names")\
                .select("*")\
                .eq("role", "лидер")\
                .execute().data
            
            for user in user_leaders:
                user['player_type'] = 'telegram'
            for fake in fake_leaders:
                fake['player_type'] = 'fake'
            
            return user_leaders + fake_leaders
        except Exception as e:
            print(f"Error getting leaders: {e}")
            return []

    async def get_soldiers(self) -> List[Dict]:
        """Получить всех солдат (реальные + фиктивные)"""
        try:
            user_soldiers = self.client.table("users")\
                .select("*")\
                .eq("role", "солдат")\
                .execute().data
            
            fake_soldiers = self.client.table("fake_names")\
                .select("*")\
                .eq("role", "солдат")\
                .execute().data
            
            for user in user_soldiers:
                user['player_type'] = 'telegram'
            for fake in fake_soldiers:
                fake['player_type'] = 'fake'
            
            return user_soldiers + fake_soldiers
        except Exception as e:
            print(f"Error getting soldiers: {e}")
            return []

    async def get_regular_members(self) -> List[Dict]:
        """Получить обычных участников (реальные + фиктивные)"""
        try:
            user_members = self.client.table("users")\
                .select("*")\
                .eq("role", "участник")\
                .execute().data
            
            fake_members = self.client.table("fake_names")\
                .select("*")\
                .eq("role", "участник")\
                .execute().data
            
            for user in user_members:
                user['player_type'] = 'telegram'
            for fake in fake_members:
                fake['player_type'] = 'fake'
            
            return user_members + fake_members
        except Exception as e:
            print(f"Error getting regular members: {e}")
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
            admin_data = {"tg_id": tg_id, "username": username}
            response = self.client.table("admins").insert(admin_data).execute()
            
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