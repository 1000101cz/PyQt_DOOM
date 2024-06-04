import pygame as pg
import pathlib as pl


class Sound:
    def __init__(self, game):
        self.game = game
        pg.mixer.init()
        self.path = str(pl.Path(__file__).parent / 'resources' / 'sound')
        self.shotgun = pg.mixer.Sound(str(pl.Path(self.path) / 'shotgun.wav'))
        self.npc_pain = pg.mixer.Sound(str(pl.Path(self.path) / 'npc_pain.wav'))
        self.npc_death = pg.mixer.Sound(str(pl.Path(self.path) / 'npc_death.wav'))
        self.npc_shot = pg.mixer.Sound(str(pl.Path(self.path) / 'npc_attack.wav'))
        self.npc_shot.set_volume(0.2)
        self.player_pain = pg.mixer.Sound(str(pl.Path(self.path) / 'player_pain.wav'))
        self.theme = pg.mixer.music.load(str(pl.Path(self.path) / 'theme.mp3'))
        pg.mixer.music.set_volume(0.3)
