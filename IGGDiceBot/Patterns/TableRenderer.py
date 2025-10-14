# AdvancedPILRenderer.py
from typing import Dict, List
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
import tempfile
import os
from Patterns.Pattern import Pattern

class TableRenderer:
    def __init__(self):
        self.font = self._load_emoji_font()
        self.colors = {
            'leader': '#90EE90',
            'soldier': '#FFA500', 
            'updated': '#ADD8E6',
            'default': '#FFFFFF',
            'header': '#F0F0F0',
            'nopattern': '#FFCCCC',
            'border': '#000000'
        }
    
    def _load_emoji_font(self):
        """Загружаем шрифт с поддержкой эмодзи"""
        try:
            # Пробуем разные шрифты
            font_paths = [
                # Попробуем системные шрифты
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, 16)
            
            # Если системные не нашли, загружаем из интернета
            return self._download_font()
            
        except Exception as e:
            print(f"Ошибка загрузки шрифта: {e}")
            return ImageFont.load_default()
    
    def _download_font(self):
        """Скачиваем шрифт с поддержкой эмодзи"""
        font_url = "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf"
        
        try:
            temp_dir = tempfile.gettempdir()
            font_path = os.path.join(temp_dir, "NotoColorEmoji.ttf")
            
            if not os.path.exists(font_path):
                response = requests.get(font_url, timeout=30)
                with open(font_path, 'wb') as f:
                    f.write(response.content)
            
            return ImageFont.truetype(font_path, 16)
        except:
            return ImageFont.load_default()
    
    def create_table_image(self, pattern: Pattern, grouped_players: Dict[str, List[str]], 
                          leaders: List[str], soldiers: List[str], updated_players: List[str]) -> BytesIO:
        """Создание таблицы с улучшенной поддержкой Unicode"""
        
        if 'NOPATTERN' in grouped_players and grouped_players['NOPATTERN']:
            columns = pattern.pattern_elements + ['NOPATTERN']
        else:
            columns = pattern.pattern_elements
        
        max_rows = max(len(players) for players in grouped_players.values()) if grouped_players else 0
        num_cols = len(columns)
        num_rows = max(1, max_rows) + 1
        
        # Автоматически подбираем размеры
        cell_width = 200
        cell_height = 60
        
        img_width = num_cols * cell_width + 10
        img_height = num_rows * cell_height + 10
        
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Рисуем заголовки
        for col_idx, column in enumerate(columns):
            x = col_idx * cell_width + 5
            y = 5
            
            bg_color = self.colors['nopattern'] if column == 'NOPATTERN' else self.colors['header']
            draw.rectangle([x, y, x + cell_width - 10, y + cell_height - 10], 
                          fill=bg_color, outline=self.colors['border'], width=2)
            
            # Текст заголовка
            bbox = draw.textbbox((0, 0), column, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (cell_width - 10 - text_width) // 2
            text_y = y + 15
            
            draw.text((text_x, text_y), column, fill='black', font=self.font)
        
        # Рисуем данные
        for col_idx, column in enumerate(columns):
            players = grouped_players.get(column, [])
            
            for row_idx in range(max_rows):
                x = col_idx * cell_width + 5
                y = (row_idx + 1) * cell_height + 5
                
                player_name = players[row_idx] if row_idx < len(players) else ""
                
                # Определяем цвет
                if player_name:
                    if player_name in leaders:
                        bg_color = self.colors['leader']
                    elif player_name in soldiers:
                        bg_color = self.colors['soldier']
                    elif player_name in updated_players:
                        bg_color = self.colors['updated']
                    else:
                        bg_color = self.colors['default']
                else:
                    bg_color = self.colors['default']
                
                # Рисуем ячейку
                draw.rectangle([x, y, x + cell_width - 10, y + cell_height - 10], 
                              fill=bg_color, outline=self.colors['border'], width=1)
                
                if player_name:
                    # Обрезаем длинный текст
                    display_text = player_name
                    max_width = cell_width - 20
                    
                    # Проверяем ширину текста
                    bbox = draw.textbbox((0, 0), display_text, font=self.font)
                    text_width = bbox[2] - bbox[0]
                    
                    if text_width > max_width:
                        # Поиск оптимальной длины
                        for i in range(len(player_name)-3, 0, -1):
                            trial_text = player_name[:i] + "..."
                            bbox = draw.textbbox((0, 0), trial_text, font=self.font)
                            if bbox[2] - bbox[0] <= max_width:
                                display_text = trial_text
                                break
                    
                    # Центрируем текст
                    bbox = draw.textbbox((0, 0), display_text, font=self.font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    text_x = x + (cell_width - 10 - text_width) // 2
                    text_y = y + (cell_height - 10 - text_height) // 2
                    
                    draw.text((text_x, text_y), display_text, fill='black', font=self.font)
        
        buf = BytesIO()
        img.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        return buf
    
    def group_players_by_pattern(self, players: List[Dict], pattern: Pattern) -> Dict[str, List[str]]:
        grouped = {element: [] for element in pattern.pattern_elements}
        grouped['NOPATTERN'] = []
        remaining_players = players.copy()
        
        for element, patterns_list in zip(pattern.pattern_elements, pattern.pattern_mas_elements):
            matched_players = []
            for player in remaining_players[:]:
                player_name = player.get('player_name', '')
                if any(pattern_text and pattern_text.lower() in player_name.lower() 
                      for pattern_text in patterns_list if pattern_text):
                    matched_players.append(player_name)
                    remaining_players.remove(player)
            
            grouped[element] = matched_players
        
        grouped['NOPATTERN'] = [player.get('player_name', '') for player in remaining_players]
        return grouped