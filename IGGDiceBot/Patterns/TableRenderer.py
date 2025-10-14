# ImprovedPILRenderer.py
from typing import Dict, List
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
import tempfile
import os
from Patterns.Pattern import Pattern

class TableRenderer:
    def __init__(self):
        self.font_path = self._get_emoji_font()
        self.colors = {
            'leader': '#90EE90',
            'soldier': '#FFA500', 
            'updated': '#ADD8E6',
            'default': '#FFFFFF',
            'header': '#F0F0F0',
            'nopattern': '#FFCCCC',
            'border': '#000000'
        }
    
    def _get_emoji_font(self):
        """Получаем путь к шрифту с поддержкой эмодзи"""
        # Попробуем найти системные шрифты с поддержкой эмодзи
        system_fonts = [
            "seguiemj.ttf",  # Windows Segoe UI Emoji
            "Apple Color Emoji.ttf",  # Mac
            "NotoColorEmoji.ttf",  # Linux
            "arial.ttf"  # Fallback
        ]
        
        # Стандартные пути к шрифтам
        font_dirs = [
            "C:/Windows/Fonts",
            "/System/Library/Fonts",
            "/usr/share/fonts",
            "/Library/Fonts"
        ]
        
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for font_file in system_fonts:
                    font_path = os.path.join(font_dir, font_file)
                    if os.path.exists(font_path):
                        return font_path
        
        return None
    
    def create_table_image(self, pattern: Pattern, grouped_players: Dict[str, List[str]], 
                          leaders: List[str], soldiers: List[str], updated_players: List[str]) -> BytesIO:
        """Создание таблицы с улучшенной поддержкой эмодзи"""
        
        # Добавляем столбец NOPATTERN
        if 'NOPATTERN' in grouped_players and grouped_players['NOPATTERN']:
            columns = pattern.pattern_elements + ['NOPATTERN']
        else:
            columns = pattern.pattern_elements
        
        # Определяем размеры
        max_rows = max(len(players) for players in grouped_players.values()) if grouped_players else 0
        num_cols = len(columns)
        num_rows = max(1, max_rows) + 1  # Минимум 1 строка данных + заголовок
        
        # Параметры
        cell_width = 220
        cell_height = 70
        font_size = 16
        border = 2
        
        # Размер изображения
        img_width = num_cols * cell_width + border
        img_height = num_rows * cell_height + border
        
        # Создаем изображение
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Загружаем шрифт
        try:
            if self.font_path:
                font = ImageFont.truetype(self.font_path, font_size)
            else:
                # Пытаемся использовать любой доступный шрифт
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Функция для измерения текста
        def get_text_size(text):
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
            except:
                return len(text) * 10, 20
        
        # Рисуем заголовки
        for col_idx, column in enumerate(columns):
            x = col_idx * cell_width
            y = 0
            
            # Цвет фона
            bg_color = self.colors['nopattern'] if column == 'NOPATTERN' else self.colors['header']
            draw.rectangle([x, y, x + cell_width, y + cell_height], 
                          fill=bg_color, outline=self.colors['border'], width=border)
            
            # Текст заголовка
            text_width, text_height = get_text_size(column)
            text_x = x + (cell_width - text_width) // 2
            text_y = y + (cell_height - text_height) // 2
            
            draw.text((text_x, text_y), column, fill='black', font=font)
        
        # Рисуем данные
        for col_idx, column in enumerate(columns):
            players = grouped_players.get(column, [])
            
            for row_idx in range(max_rows):
                x = col_idx * cell_width
                y = (row_idx + 1) * cell_height
                
                player_name = players[row_idx] if row_idx < len(players) else ""
                
                # Определяем цвет
                if player_name in leaders:
                    bg_color = self.colors['leader']
                elif player_name in soldiers:
                    bg_color = self.colors['soldier']
                elif player_name in updated_players:
                    bg_color = self.colors['updated']
                else:
                    bg_color = self.colors['default']
                
                # Рисуем ячейку
                draw.rectangle([x, y, x + cell_width, y + cell_height], 
                              fill=bg_color, outline=self.colors['border'], width=border)
                
                if player_name:
                    # Обрезаем текст если не помещается
                    max_text_width = cell_width - 20
                    display_text = player_name
                    text_width, text_height = get_text_size(display_text)
                    
                    if text_width > max_text_width:
                        # Постепенно обрезаем текст
                        for i in range(len(player_name)-3, 0, -1):
                            trial_text = player_name[:i] + "..."
                            trial_width, _ = get_text_size(trial_text)
                            if trial_width <= max_text_width:
                                display_text = trial_text
                                break
                    
                    # Центрируем текст
                    text_width, text_height = get_text_size(display_text)
                    text_x = x + (cell_width - text_width) // 2
                    text_y = y + (cell_height - text_height) // 2
                    
                    draw.text((text_x, text_y), display_text, fill='black', font=font)
        
        # Сохраняем
        buf = BytesIO()
        img.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        return buf
    
    def group_players_by_pattern(self, players: List[Dict], pattern: Pattern) -> Dict[str, List[str]]:
        """Логика группировки"""
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