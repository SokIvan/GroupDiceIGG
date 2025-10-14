# WeasyPrintRenderer.py
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from io import BytesIO
from typing import Dict, List
from Patterns.Pattern import Pattern
import tempfile
import os

class WeasyPrintRenderer:
    def __init__(self):
        self.colors = {
            'leader': '#90EE90',
            'soldier': '#FFA500', 
            'updated': '#ADD8E6',
            'default': '#FFFFFF',
            'header': '#F0F0F0',
            'nopattern': '#FFCCCC'
        }
    
    def create_table_image(self, pattern: Pattern, grouped_players: Dict[str, List[str]], 
                          leaders: List[str], soldiers: List[str], updated_players: List[str]) -> BytesIO:
        """Создание таблицы через WeasyPrint"""
        
        if 'NOPATTERN' in grouped_players and grouped_players['NOPATTERN']:
            columns = pattern.pattern_elements + ['NOPATTERN']
        else:
            columns = pattern.pattern_elements
        
        html_content = self._create_html_table(columns, grouped_players, leaders, soldiers, updated_players)
        
        try:
            font_config = FontConfiguration()
            css = CSS(string='''
                @font-face {
                    font-family: 'EmojiFont';
                    src: local('Apple Color Emoji'), 
                         local('Segoe UI Emoji'), 
                         local('Noto Color Emoji');
                }
                body {
                    font-family: 'EmojiFont', sans-serif;
                }
            ''', font_config=font_config)
            
            html = HTML(string=html_content)
            buf = BytesIO()
            
            html.write_png(buf, stylesheets=[css], font_config=font_config)
            buf.seek(0)
            return buf
            
        except Exception as e:
            print(f"Ошибка WeasyPrint: {e}")
            return self._create_fallback_image(columns, grouped_players)
    
    def _create_html_table(self, columns, grouped_players, leaders, soldiers, updated_players):
        max_rows = max(len(players) for players in grouped_players.values()) if grouped_players else 0
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&family=Noto+Sans:wght@400;700&display=swap');
        
        body {{
            margin: 0;
            padding: 20px;
            font-family: "Noto Color Emoji", "Apple Color Emoji", "Segoe UI Emoji", "Noto Sans", sans-serif;
            font-size: 14px;
        }}
        
        .table-container {{
            width: 100%;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            border: 2px solid #000;
        }}
        
        th, td {{
            border: 1px solid #000;
            padding: 12px;
            text-align: center;
            min-width: 150px;
            max-width: 200px;
            word-wrap: break-word;
        }}
        
        th {{
            font-weight: bold;
            font-size: 16px;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
    <div class="table-container">
        <table>
            <thead>
                <tr>
'''
        
        # Заголовки
        for column in columns:
            bg_color = self.colors['nopattern'] if column == 'NOPATTERN' else self.colors['header']
            html += f'<th style="background-color: {bg_color};">{self._escape_html(column)}</th>'
        
        html += '''
                </tr>
            </thead>
            <tbody>
'''
        
        # Данные
        for i in range(max_rows):
            html += '<tr>'
            for column in columns:
                players = grouped_players.get(column, [])
                player_name = players[i] if i < len(players) else ''
                
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
                
                html += f'<td style="background-color: {bg_color};">{self._escape_html(player_name)}</td>'
            
            html += '</tr>'
        
        html += '''
            </tbody>
        </table>
    </div>
</body>
</html>'''
        return html
    
    def _escape_html(self, text):
        """Экранирование HTML"""
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                  .replace('<', '&lt;')
                  .replace('>', '&gt;')
                  .replace('"', '&quot;'))
    
    def _create_fallback_image(self, columns, grouped_players):
        from PIL import Image, ImageDraw
        
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        y = 10
        for col in columns:
            players = grouped_players.get(col, [])
            draw.text((10, y), f"=== {col} ===", fill='black')
            y += 20
            for player in players[:5]:
                draw.text((20, y), player, fill='black')
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