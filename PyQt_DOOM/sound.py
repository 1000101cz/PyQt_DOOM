import pygame as pg
import pathlib as pl


class Sound:
    def __init__(self, game, settings):
        self.game = game
        pg.mixer.init()

        if settings.original_pack:
            self.path = str(pl.Path(__file__).parent / 'resources' / 'sound')
        else:
            self.path = str(pl.Path(__file__).parent / 'resources_alt' / 'sound')

        self.shotgun = pg.mixer.Sound(str(pl.Path(self.path) / 'shotgun.wav'))
        self.shotgun.set_volume(settings.volume_weapon * settings.volume_master)

        self.npc_pain = pg.mixer.Sound(str(pl.Path(self.path) / 'npc_pain.wav'))  # soldier / greta
        self.npc_pain.set_volume(settings.volume_enemies * settings.volume_master)
        self.npc_pain2 = pg.mixer.Sound(str(pl.Path(self.path) / 'npc_pain2.wav'))  # monsters
        self.npc_pain2.set_volume(settings.volume_enemies * settings.volume_master)

        self.npc_death = pg.mixer.Sound(str(pl.Path(self.path) / 'npc_death.wav'))
        self.npc_death.set_volume(settings.volume_enemies * settings.volume_master)

        self.npc_shot = pg.mixer.Sound(str(pl.Path(self.path) / 'npc_attack.wav'))
        self.npc_shot.set_volume(0.2 * settings.volume_enemies * settings.volume_master)

        self.player_pain = pg.mixer.Sound(str(pl.Path(self.path) / 'player_pain.wav'))
        self.player_pain.set_volume(settings.volume_player * settings.volume_master)

        self.victory = pg.mixer.Sound(str(pl.Path(self.path) / 'victory.wav'))
        self.victory.set_volume(settings.volume_master)

        self.lose = pg.mixer.Sound(str(pl.Path(self.path) / 'lose.wav'))
        self.lose.set_volume(settings.volume_master)

        self.theme = pg.mixer.music.load(str(pl.Path(self.path) / 'theme.mp3'))
        pg.mixer.music.set_volume(0.3 * settings.volume_music * settings.volume_master)
