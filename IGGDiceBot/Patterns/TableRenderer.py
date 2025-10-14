# AlternativeTableRenderer.py

import cairosvg
from io import BytesIO
from typing import Dict, List
from Patterns.Pattern import Pattern

class TableRenderer:
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
        """Создание таблицы через SVG/HTML для идеальной поддержки эмодзи"""
        
        # Добавляем столбец NOPATTERN
        if 'NOPATTERN' in grouped_players and grouped_players['NOPATTERN']:
            columns = pattern.pattern_elements + ['NOPATTERN']
        else:
            columns = pattern.pattern_elements
        
        # Создаем HTML таблицу
        html_content = self._create_html_table(columns, grouped_players, leaders, soldiers, updated_players)
        
        # Конвертируем HTML в PNG через SVG
        svg_content = f'''
        <svg width="1000" height="600" xmlns="http://www.w3.org/2000/svg">
            <foreignObject width="100%" height="100%">
                <div xmlns="http://www.w3.org/1999/xhtml">
                    {html_content}
                </div>
            </foreignObject>
        </svg>
        '''
        
        buf = BytesIO()
        cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=buf)
        buf.seek(0)
        return buf
    
    def _create_html_table(self, columns, grouped_players, leaders, soldiers, updated_players):
        """Создает HTML таблицу"""
        
        max_rows = max(len(players) for players in grouped_players.values())
        
        html = '''
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
                font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif;
                font-size: 14px;
            }
            th, td {
                border: 1px solid black;
                padding: 8px;
                text-align: center;
                max-width: 200px;
                word-wrap: break-word;
            }
            th {
                background-color: #F0F0F0;
                font-weight: bold;
            }
        </style>
        <table>
        '''
        
        # Заголовки
        html += '<tr>'
        for column in columns:
            bg_color = self.colors['nopattern'] if column == 'NOPATTERN' else self.colors['header']
            html += f'<th style="background-color: {bg_color}">{column}</th>'
        html += '</tr>'
        
        # Данные
        for i in range(max_rows):
            html += '<tr>'
            for column in columns:
                players = grouped_players.get(column, [])
                player_name = players[i] if i < len(players) else ''
                
                # Определяем цвет
                if player_name in leaders:
                    bg_color = self.colors['leader']
                elif player_name in soldiers:
                    bg_color = self.colors['soldier']
                elif player_name in updated_players:
                    bg_color = self.colors['updated']
                else:
                    bg_color = self.colors['default']
                
                html += f'<td style="background-color: {bg_color}">{player_name}</td>'
            html += '</tr>'
        
        html += '</table>'
        return html
    
    def group_players_by_pattern(self, players: List[Dict], pattern: Pattern) -> Dict[str, List[str]]:
        """Та же логика группировки"""
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