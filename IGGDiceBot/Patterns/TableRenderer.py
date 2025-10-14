# RenderCompatibleRenderer.py
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from typing import Dict, List
from Patterns.Pattern import Pattern
from PIL import Image
import base64

class TableRenderer:
    def __init__(self):
        self.setup_styles()
        self.colors = {
            'leader': '#90EE90',
            'soldier': '#FFA500', 
            'updated': '#ADD8E6',
            'default': 'white',
            'header': '#F0F0F0',
            'nopattern': '#FFCCCC'
        }
    
    def setup_styles(self):
        """Настройка для Render.com"""
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['svg.fonttype'] = 'none'
    
    def create_table_image(self, pattern: Pattern, grouped_players: Dict[str, List[str]], 
                          leaders: List[str], soldiers: List[str], updated_players: List[str]) -> BytesIO:
        """Основной метод с fallback"""
        try:
            return self._create_with_matplotlib(pattern, grouped_players, leaders, soldiers, updated_players)
        except Exception as e:
            print(f"Matplotlib failed: {e}")
            return self._create_with_pil_fallback(pattern, grouped_players, leaders, soldiers, updated_players)
    
    def _create_with_matplotlib(self, pattern, grouped_players, leaders, soldiers, updated_players):
        """Пытаемся использовать matplotlib"""
        if 'NOPATTERN' in grouped_players:
            columns = pattern.pattern_elements + ['NOPATTERN']
        else:
            columns = pattern.pattern_elements
        
        max_rows = max(len(players) for players in grouped_players.values())
        data = {}
        
        for col in columns:
            players_list = grouped_players.get(col, [])
            players_list.extend([''] * (max_rows - len(players_list)))
            data[col] = players_list
        
        df = pd.DataFrame(data)
        
        fig, ax = plt.subplots(figsize=(len(columns) * 1.5, max_rows * 0.4 + 1))
        ax.axis('tight')
        ax.axis('off')
        
        table = plt.table(cellText=df.values,
                         colLabels=df.columns,
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 2)
        
        # Цвета
        for i in range(len(df.columns)):
            header_color = self.colors['nopattern'] if df.columns[i] == 'NOPATTERN' else self.colors['header']
            table[(0, i)].set_facecolor(header_color)
            table[(0, i)].set_text_props(weight='bold')
            
            for j in range(len(df)):
                cell_value = df.iloc[j, i]
                if cell_value.strip():
                    if cell_value in leaders:
                        color = self.colors['leader']
                    elif cell_value in soldiers:
                        color = self.colors['soldier']
                    elif cell_value in updated_players:
                        color = self.colors['updated']
                    else:
                        color = self.colors['default']
                    table[(j+1, i)].set_facecolor(color)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close()
        return buf
    
    def _create_with_pil_fallback(self, pattern, grouped_players, leaders, soldiers, updated_players):
        """Fallback на чистый PIL"""
        from PIL import Image, ImageDraw
        
        if 'NOPATTERN' in grouped_players:
            columns = pattern.pattern_elements + ['NOPATTERN']
        else:
            columns = pattern.pattern_elements
        
        img = Image.new('RGB', (1000, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        # Простой текст
        y = 10
        for col in columns:
            players = grouped_players.get(col, [])
            draw.text((10, y), f"=== {col} ===", fill='black')
            y += 20
            for player in players[:10]:  # Ограничиваем количество
                color = 'black'
                if player in leaders:
                    color = 'green'
                elif player in soldiers:
                    color = 'orange'
                elif player in updated_players:
                    color = 'blue'
                
                draw.text((20, y), player, fill=color)
                y += 15
            y += 10
        
        buf = BytesIO()
        img.save(buf, format='PNG')
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