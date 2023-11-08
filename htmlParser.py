from collections.abc import Iterable
from bs4 import BeautifulSoup

sandbox = ['sandbox', 'open-world', 'free-roaming']
RTS = ['real-time strategy', 'strategy', 'RTS']
shooters = ['FPS', 'first-person shooter', 'TPS', 'third-person shooter', 'shooters']
multiplayer_online_battle_arena = ['Multiplayer online battle arena', 'MOBA']
role_playing = ['RPG', 'role playing', 'role-playing', 'ARPG']
simulation_and_sports = ['sport', 'simulation']
puzzlers_and_party = ['puzzle', 'party', 'minigames']
survival_and_horror = ['survival', 'horror']
platformer = ['platformer']
genres = [sandbox, RTS, shooters, 
          multiplayer_online_battle_arena, role_playing, 
          simulation_and_sports, puzzlers_and_party, survival_and_horror, platformer]

class htmlParser:
    def parse(html):
        genre_names = ['sandbox', 'RTS', 'shooters', 'multiplayer_online_battle_arena', 'role_playing', 'simulation_and_sports', 'puzzlers_and_party', 'survival_and_horror', 'platformer']
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(" ", strip=True).lower()
        
        counts = dict.fromkeys(genre_names, 0)
        for genre in genres:
            genre_name = genre_names.pop()
            for keyword in genre:
                counts[genre_name] += text.count(keyword.lower())
        return counts
                
        

                
        
        