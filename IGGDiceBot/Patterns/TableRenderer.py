from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
from io import BytesIO
from PIL import Image

from Patterns.Pattern import Pattern

class TableRenderer:
    def __init__(self):
        self.setup_styles()
    
    def setup_styles(self):
        """Настройка стилей для таблицы"""
        plt.rcParams['font.family'] = 'DejaVu Sans'
        self.colors = {
            'leader': '#90EE90',  # зеленый
            'soldier': '#FFA500', # оранжевый
            'updated': '#ADD8E6', # синий
            'default': '#FFFFFF', # белый
            'header': '#F0F0F0',  # серый для шапки
            'border': '#000000'   # черный
        }
    
    def classify_player(self, player_name: str, leaders: List[str], soldiers: List[str], updated_players: List[str]) -> str:
        """Классификация игрока для определения цвета"""
        if player_name in leaders:
            return 'leader'
        elif player_name in soldiers:
            return 'soldier'
        elif player_name in updated_players:
            return 'updated'
        else:
            return 'default'
    
    def create_table_image(self, pattern: Pattern, grouped_players: Dict[str, List[str]], 
                          leaders: List[str], soldiers: List[str], updated_players: List[str]) -> BytesIO:
        """Создание таблицы как изображения"""
        
        # Создаем DataFrame для таблицы
        max_rows = max(len(players) for players in grouped_players.values()) if grouped_players else 0
        data = {}
        
        for element in pattern.pattern_elements:
            players = grouped_players.get(element, [])
            # Дополняем пустыми значениями до максимальной длины
            players.extend([''] * (max_rows - len(players)))
            data[element] = players
        
        df = pd.DataFrame(data)
        
        # Создаем фигуру
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('tight')
        ax.axis('off')
        
        # Создаем таблицу
        table = ax.table(cellText=df.values,
                        colLabels=df.columns,
                        cellLoc='center',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        # Стилизация таблицы
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        
        # Цвета для ячеек
        for i in range(len(df.columns)):
            # Шапка
            table[(0, i)].set_facecolor(self.colors['header'])
            table[(0, i)].set_text_props(weight='bold')
        
        for i in range(len(df)):
            for j in range(len(df.columns)):
                cell_value = df.iloc[i, j]
                if cell_value:  # Если ячейка не пустая
                    color_type = self.classify_player(cell_value, leaders, soldiers, updated_players)
                    table[(i+1, j)].set_face_color(self.colors[color_type])
        
        # Сохраняем в BytesIO
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', pad_inches=0.1)
        buf.seek(0)
        plt.close()
        
        # Обрезаем лишнее пространство
        img = Image.open(buf)
        img = img.crop(img.getbbox())  # Авто-обрезка
        output_buf = BytesIO()
        img.save(output_buf, format='PNG')
        output_buf.seek(0)
        
        return output_buf

    def group_players_by_pattern(self, players: List[Dict], pattern: Pattern) -> Dict[str, List[str]]:
        """Группировка игроков по паттерну"""
        grouped = {element: [] for element in pattern.pattern_elements}
        remaining_players = players.copy()
        
        # Сортируем игроков по паттерну
        for element, patterns_list in zip(pattern.pattern_elements, pattern.pattern_mas_elements):
            matched_players = []
            for player in remaining_players[:]:
                player_name = player.get('player_name', '')
                if any(pattern.lower() in player_name.lower() for pattern in patterns_list):
                    matched_players.append(player_name)
                    remaining_players.remove(player)
            
            grouped[element] = matched_players
        
        return grouped