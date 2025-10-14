# TableRenderer.py - радикальное решение для смайликов

from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
import os
import tempfile

from Patterns.Pattern import Pattern

class TableRenderer:
    def __init__(self):
        self.emoji_font_path = self.download_emoji_font()
        self.setup_styles()
    
    def download_emoji_font(self):
        """Скачиваем и устанавливаем шрифт с поддержкой эмодзи"""
        font_urls = [
            "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf",
            "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoEmoji-VariableFont_wght.ttf",
            "https://cdn.jsdelivr.net/npm/twemoji-colr-font@latest/twemoji.ttf"
        ]
        
        temp_dir = tempfile.gettempdir()
        
        for font_url in font_urls:
            try:
                font_name = os.path.basename(font_url)
                font_path = os.path.join(temp_dir, font_name)
                
                if not os.path.exists(font_path):
                    print(f"Скачиваем шрифт {font_name}...")
                    response = requests.get(font_url, timeout=30)
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                
                # Проверяем, что шрифт загружен в matplotlib
                if any(os.path.basename(f) == font_name for f in fm.findSystemFonts()):
                    return font_path
                    
            except Exception as e:
                print(f"Ошибка загрузки шрифта {font_url}: {e}")
                continue
        
        # Если не удалось скачать, используем системные шрифты
        system_fonts = [
            "Segoe UI Emoji", 
            "Apple Color Emoji",
            "Noto Color Emoji",
            "Android Emoji",
            "Twemoji",
            "DejaVu Sans"
        ]
        
        for font_name in system_fonts:
            if any(f.name == font_name for f in fm.fontManager.ttflist):
                return None  # Используем системный шрифт
        
        return None
    
    def setup_styles(self):
        """Настройка стилей с поддержкой эмодзи"""
        if self.emoji_font_path:
            # Регистрируем скачанный шрифт
            fm.fontManager.addfont(self.emoji_font_path)
            font_name = os.path.basename(self.emoji_font_path).replace('.ttf', '')
            plt.rcParams['font.family'] = font_name
        else:
            # Пытаемся использовать системные шрифты с поддержкой эмодзи
            emoji_fonts = ['Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 'DejaVu Sans']
            for font in emoji_fonts:
                if any(f.name == font for f in fm.fontManager.ttflist):
                    plt.rcParams['font.family'] = font
                    break
        
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['svg.fonttype'] = 'none'
        
        self.colors = {
            'leader': '#90EE90',
            'soldier': '#FFA500', 
            'updated': '#ADD8E6',
            'default': '#FFFFFF',
            'header': '#F0F0F0',
            'nopattern': '#FFCCCC',
            'border': '#000000'
        }
    
    def create_table_image_pil(self, pattern: Pattern, grouped_players: Dict[str, List[str]], 
                              leaders: List[str], soldiers: List[str], updated_players: List[str]) -> BytesIO:
        """Создание таблицы используя PIL для лучшей поддержки Unicode"""
        
        # Добавляем столбец NOPATTERN
        if 'NOPATTERN' in grouped_players and grouped_players['NOPATTERN']:
            columns = pattern.pattern_elements + ['NOPATTERN']
        else:
            columns = pattern.pattern_elements
        
        # Определяем размеры таблицы
        max_rows = max(len(players) for players in grouped_players.values()) if grouped_players else 0
        num_cols = len(columns)
        num_rows = max_rows + 1  # +1 для заголовка
        
        # Параметры ячеек
        cell_width = 200
        cell_height = 60
        font_size = 14
        border_width = 2
        
        # Рассчитываем размер изображения
        img_width = num_cols * cell_width + border_width
        img_height = num_rows * cell_height + border_width
        
        # Создаем изображение
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Пытаемся загрузить шрифт с поддержкой эмодзи
            if self.emoji_font_path and os.path.exists(self.emoji_font_path):
                font = ImageFont.truetype(self.emoji_font_path, font_size)
            else:
                # Используем дефолтный шрифт PIL который поддерживает базовые эмодзи
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Рисуем заголовки
        for col_idx, column in enumerate(columns):
            x = col_idx * cell_width
            y = 0
            
            # Фон заголовка
            header_color = self.colors['nopattern'] if column == 'NOPATTERN' else self.colors['header']
            draw.rectangle([x, y, x + cell_width, y + cell_height], fill=header_color, outline='black')
            
            # Текст заголовка
            bbox = draw.textbbox((0, 0), column, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x + (cell_width - text_width) // 2
            text_y = y + (cell_height - text_height) // 2
            
            draw.text((text_x, text_y), column, fill='black', font=font)
        
        # Рисуем данные
        for col_idx, column in enumerate(columns):
            players_list = grouped_players.get(column, [])
            
            for row_idx, player_name in enumerate(players_list):
                if row_idx >= max_rows:
                    break
                    
                x = col_idx * cell_width
                y = (row_idx + 1) * cell_height
                
                # Определяем цвет ячейки
                if player_name in leaders:
                    cell_color = self.colors['leader']
                elif player_name in soldiers:
                    cell_color = self.colors['soldier']
                elif player_name in updated_players:
                    cell_color = self.colors['updated']
                else:
                    cell_color = self.colors['default']
                
                # Рисуем ячейку
                draw.rectangle([x, y, x + cell_width, y + cell_height], 
                              fill=cell_color, outline='black')
                
                # Текст игрока
                bbox = draw.textbbox((0, 0), player_name, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width > cell_width - 10:  # Если текст не помещается
                    # Обрезаем текст и добавляем "..."
                    max_chars = len(player_name) * (cell_width - 30) // text_width
                    display_text = player_name[:max_chars-3] + "..." if len(player_name) > max_chars else player_name
                else:
                    display_text = player_name
                
                bbox = draw.textbbox((0, 0), display_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = x + (cell_width - text_width) // 2
                text_y = y + (cell_height - text_height) // 2
                
                draw.text((text_x, text_y), display_text, fill='black', font=font)
        
        # Сохраняем в BytesIO
        buf = BytesIO()
        img.save(buf, format='PNG', optimize=True)
        buf.seek(0)
        return buf
    
    def create_table_image(self, pattern: Pattern, grouped_players: Dict[str, List[str]], 
                          leaders: List[str], soldiers: List[str], updated_players: List[str]) -> BytesIO:
        """Основной метод создания таблицы (использует PIL)"""
        return self.create_table_image_pil(pattern, grouped_players, leaders, soldiers, updated_players)
    
    def group_players_by_pattern(self, players: List[Dict], pattern: Pattern) -> Dict[str, List[str]]:
        """Группировка игроков по паттерну с добавлением NOPATTERN"""
        grouped = {element: [] for element in pattern.pattern_elements}
        grouped['NOPATTERN'] = []
        remaining_players = players.copy()
        
        # Сортируем игроков по паттерну
        for element, patterns_list in zip(pattern.pattern_elements, pattern.pattern_mas_elements):
            matched_players = []
            for player in remaining_players[:]:
                player_name = player.get('player_name', '')
                # Проверяем все паттерны в списке
                if any(pattern_text and pattern_text.lower() in player_name.lower() 
                      for pattern_text in patterns_list if pattern_text):
                    matched_players.append(player_name)
                    remaining_players.remove(player)
            
            grouped[element] = matched_players
        
        # Все оставшиеся игроки попадают в NOPATTERN
        grouped['NOPATTERN'] = [player.get('player_name', '') for player in remaining_players]
        
        return grouped