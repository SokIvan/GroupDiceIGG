class PatternManager:
    def __init__(self, db: Database):
        self.db = db
    
    async def get_active_pattern(self) -> Pattern:
        """Получить активный паттерн"""
        response = await self.db.client.table('Table_Patterns')\
            .select('*')\
            .eq('status', 'Active')\
            .execute()
        
        if response.data:
            return Pattern.from_db(response.data[0])
        return None
    
    async def set_active_pattern(self, pattern_id: int):
        """Установить активный паттерн"""
        # Сначала сбрасываем все статусы
        await self.db.client.table('Table_Patterns')\
            .update({'status': 'Disable'})\
            .execute()
        
        # Устанавливаем новый активный
        await self.db.client.table('Table_Patterns')\
            .update({'status': 'Active', 'updated_at': 'now()'})\
            .eq('id', pattern_id)\
            .execute()
    
    async def create_pattern(self, pattern_name: str, pattern_elements: List[str], pattern_mas_elements: List[List[str]]):
        """Создать новый паттерн"""
        pattern_data = {
            'pattern_name': pattern_name,
            'pattern_elements': ','.join(pattern_elements),
            'pattern_mas_elements': json.dumps(pattern_mas_elements),
            'status': 'Disable'
        }
        
        response = await self.db.client.table('Table_Patterns')\
            .insert(pattern_data)\
            .execute()
        
        return response.data[0] if response.data else None
    
    async def get_all_patterns(self):
        """Получить все паттерны"""
        response = await self.db.client.table('Table_Patterns')\
            .select('*')\
            .order('created_at')\
            .execute()
        
        return [Pattern.from_db(pattern) for pattern in response.data]