import pygame as pg
import pathlib as pl
from loguru import logger


class ObjectRenderer:
    def __init__(self, game):
        s = game.settings
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        if self.game.settings.original_pack:
            resources = 'resources'
        else:
            resources = 'resources_alt'
        self.sky_image = self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / 'sky.png'), (s.resolution[0], s.HALF_HEIGHT))
        self.last_score = None
        self.sky_offset = 0
        self.blood_screen = self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / 'blood_screen.png'), s.resolution)
        self.digit_size = 90
        self.digit_images = [self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / 'digits' / f'{i}.png'), [self.digit_size] * 2) for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.game_over_image = self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / 'game_over.png'), s.resolution)
        self.win_image = self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / 'win.png'), s.resolution)

    def draw(self):
        self.draw_background()
        self.render_game_objects()
        self.draw_player_health()
        self.draw_score()

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_player_health(self):
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (i * self.digit_size, 0))
        self.screen.blit(self.digits['10'], ((i + 1) * self.digit_size, 0))

    def draw_score(self):
        WIDTH = self.game.settings.resolution[0]
        score = str(self.game.get_score())
        if self.last_score != score:
            logger.info(f"Score is {score}")
        for i, char in enumerate(score):
            if self.last_score != score:
                logger.debug(f"Char '{char}' no position ({WIDTH - (len(score) - i)*self.digit_size}, 0)")
            self.screen.blit(self.digits[char], (WIDTH-(len(score) - i)*self.digit_size, 0))
        self.last_score = score

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        s = self.game.settings
        WIDTH, HEIGHT = s.resolution
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        # floor
        pg.draw.rect(self.screen, s.FLOOR_COLOR, (0, s.HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        import pathlib as pl
        if self.game.settings.original_pack:
            resources = 'resources'
        else:
            resources = 'resources_alt'

        res = (self.game.settings.TEXTURE_SIZE, self.game.settings.TEXTURE_SIZE)

        return {
            1: self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / '1.png'), res),
            2: self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / '2.png'), res),
            3: self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / '3.png'), res),
            4: self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / '4.png'), res),
            5: self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / '5.png'), res),
            6: self.get_texture(str(pl.Path(__file__).parent / resources / 'textures' / '6.png'), res),
        }