# TableRenderer.py - обновленная версия

from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
from io import BytesIO
from PIL import Image
import os

from Patterns.Pattern import Pattern

class TableRenderer:
    def __init__(self):
        self.setup_styles()
    
    def setup_styles(self):
        """Настройка стилей для таблицы с поддержкой Unicode"""
        # Пытаемся найти шрифт, который поддерживает Unicode
        possible_fonts = [
            'DejaVu Sans', 
            'Arial Unicode MS', 
            'Microsoft Sans Serif', 
            'Liberation Sans',
            'Noto Sans',
            'Segoe UI'
        ]
        
        for font in possible_fonts:
            if any(f.name == font for f in fm.fontManager.ttflist):
                plt.rcParams['font.family'] = font
                break
        else:
            # Если не нашли подходящий шрифт, используем дефолтный
            plt.rcParams['font.family'] = 'sans-serif'
        
        # Устанавливаем параметры для поддержки Unicode
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['svg.fonttype'] = 'none'
        
        self.colors = {
            'leader': '#90EE90',  # зеленый
            'soldier': '#FFA500', # оранжевый
            'updated': '#ADD8E6', # синий
            'default': '#FFFFFF', # белый
            'header': '#F0F0F0',  # серый для шапки
            'nopattern': '#FFCCCC', # светло-красный для NOPATTERN
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
        """Создание таблицы как изображения с поддержкой NOPATTERN"""
        
        # Добавляем столбец NOPATTERN если есть игроки без паттерна
        if 'NOPATTERN' in grouped_players and grouped_players['NOPATTERN']:
            pattern_elements_with_nopattern = pattern.pattern_elements + ['NOPATTERN']
        else:
            pattern_elements_with_nopattern = pattern.pattern_elements
        
        # Создаем DataFrame для таблицы
        max_rows = max(len(players) for players in grouped_players.values()) if grouped_players else 0
        data = {}
        
        for element in pattern_elements_with_nopattern:
            players = grouped_players.get(element, [])
            # Дополняем пустыми значениями до максимальной длины
            players.extend([''] * (max_rows - len(players)))
            data[element] = players
        
        df = pd.DataFrame(data)
        
        # Создаем фигуру с учетом возможного дополнительного столбца
        fig_width = max(10, len(pattern_elements_with_nopattern) * 2)
        fig, ax = plt.subplots(figsize=(fig_width, 8))
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
        table.set_fontsize(12)  # Увеличим размер шрифта для лучшей читаемости
        table.scale(1, 1.5)
        
        # Применяем цвета ко всем ячейкам
        for i in range(len(df.columns)):
            # Шапка - окрашиваем все заголовки
            header_color = self.colors['nopattern'] if df.columns[i] == 'NOPATTERN' else self.colors['header']
            table[(0, i)].set_facecolor(header_color)
            table[(0, i)].set_text_props(weight='bold')
            
            # Ячейки данных
            for j in range(len(df)):
                cell_value = df.iloc[j, i]
                if cell_value and cell_value.strip():  # Если ячейка не пустая
                    color_type = self.classify_player(cell_value, leaders, soldiers, updated_players)
                    table[(j+1, i)].set_facecolor(self.colors[color_type])
                else:
                    # Пустые ячейки оставляем белыми
                    table[(j+1, i)].set_facecolor(self.colors['default'])
        
        # Добавляем границы для лучшей видимости
        for key, cell in table.get_celld().items():
            cell.set_edgecolor(self.colors['border'])
            cell.set_linewidth(0.5)
        
        # Сохраняем в BytesIO
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', pad_inches=0.1, 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)  # Явно закрываем фигуру
        
        # Обрезаем лишнее пространство
        img = Image.open(buf)
        img = img.crop(img.getbbox())  # Авто-обрезка
        output_buf = BytesIO()
        img.save(output_buf, format='PNG', optimize=True)
        output_buf.seek(0)
        
        return output_buf

    def group_players_by_pattern(self, players: List[Dict], pattern: Pattern) -> Dict[str, List[str]]:
        """Группировка игроков по паттерну с добавлением NOPATTERN"""
        grouped = {element: [] for element in pattern.pattern_elements}
        grouped['NOPATTERN'] = []  # Всегда добавляем столбец для игроков без паттерна
        remaining_players = players.copy()
        
        # Сортируем игроков по паттерну
        for element, patterns_list in zip(pattern.pattern_elements, pattern.pattern_mas_elements):
            matched_players = []
            for player in remaining_players[:]:
                player_name = player.get('player_name', '')
                if any(pattern.lower() in player_name.lower() for pattern in patterns_list if pattern):
                    matched_players.append(player_name)
                    remaining_players.remove(player)
            
            grouped[element] = matched_players
        
        # Все оставшиеся игроки попадают в NOPATTERN
        grouped['NOPATTERN'] = [player.get('player_name', '') for player in remaining_players]
        
        return grouped