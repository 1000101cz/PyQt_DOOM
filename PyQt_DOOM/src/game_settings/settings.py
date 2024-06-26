from time import sleep
import pathlib as pl
import pygame as pg
import random
import json
import math
import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from PyQt_DOOM.sound import Sound


_help_path = pl.Path(__file__).parent / 'settings.ui'
_help_dialog = uic.loadUiType(_help_path)[0]


_resolution_720 = 1280, 720
_resolution_900 = 1600, 900
_resolution_1080 = 1920, 1080
_resolution_1200 = 1920, 1200
_resolution_1440 = 2560, 1440
_resolutions = [_resolution_720,
                _resolution_900,
                _resolution_1080,
                _resolution_1200,
                _resolution_1440]

_fps_limits = {
    "Unlimited": 0,
    '59Hz': 59,
    '60Hz': 60,
    '120Hz': 120,
    '144Hz': 144
}


def save_json(data: dict, path: str | pl.Path) -> None:
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def load_json(path: str | pl.Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    return data


class GameSettings:
    def __init__(self, fpath: pl.Path = pl.Path(os.getenv('LOCALAPPDATA')) / 'PyQt_DOOM' / 'settings.json'):
        # unmodifiable
        self.PLAYER_POS = 1.5, 5  # mini_map
        self.PLAYER_ANGLE = 0
        self.PLAYER_SPEED = 0.004
        self.PLAYER_ROT_SPEED = 0.002
        self.PLAYER_SIZE_SCALE = 60
        self.PLAYER_MAX_HEALTH = 100
        self.MOUSE_SENSITIVITY = 0.0003
        self.MOUSE_MAX_REL = 40
        self.MOUSE_BORDER_LEFT = 100
        self.FLOOR_COLOR = (30, 30, 30)
        self.FOV = math.pi / 3
        self.HALF_FOV = self.FOV / 2
        self.MAX_DEPTH = 20
        self.TEXTURE_SIZE = 256
        self.HALF_TEXTURE_SIZE = self.TEXTURE_SIZE // 2
        self.HALF_WIDTH = None
        self.HALF_HEIGHT = None
        self.MOUSE_BORDER_RIGHT = None
        self.NUM_RAYS = None
        self.HALF_NUM_RAYS = None
        self.DELTA_ANGLE = None
        self.SCREEN_DIST = None
        self.SCALE = None

        # modifiable
        self.original_pack = False

        self.volume_master = 1.0
        self.volume_music = 1.0
        self.volume_enemies = 1.0
        self.volume_player = 1.0
        self.volume_weapon = 1.0

        self.fullscreen = False
        self.resolution = _resolution_900
        self.fps_limit = 0

        if fpath.is_file():
            self.load(fpath)
            self._prepare_static_vals()
        else:
            self._prepare_static_vals()
            self.save(fpath)

    def get_dict(self):
        return {
                'original_pack': self.original_pack,

                'volume_master': self.volume_master,
                'volume_music': self.volume_music,
                'volume_enemies': self.volume_enemies,
                'volume_player': self.volume_player,
                'volume_weapon': self.volume_weapon,

                'fullscreen': self.fullscreen,
                'res_width': self.resolution[0],
                'res_height': self.resolution[1],
                'fps_limit': self.fps_limit
            }

    def save(self, fpath: pl.Path = pl.Path(os.getenv('LOCALAPPDATA')) / 'PyQt_DOOM' / 'settings.json'):
        self._prepare_static_vals()
        the_dict = self.get_dict()
        save_json(the_dict, fpath)

    def load(self, fpath: pl.Path = pl.Path(os.getenv('LOCALAPPDATA')) / 'PyQt_DOOM' / 'settings.json'):
        the_dict = load_json(fpath)
        self.original_pack = the_dict['original_pack']

        self.volume_master = the_dict['volume_master']
        self.volume_music = the_dict['volume_music']
        self.volume_enemies = the_dict['volume_enemies']
        self.volume_player = the_dict['volume_player']
        self.volume_weapon = the_dict['volume_weapon']

        self.fullscreen = the_dict['fullscreen']
        self.resolution = the_dict['res_width'], the_dict['res_height']
        self.fps_limit = the_dict['fps_limit']

        self._prepare_static_vals()

    def HALF_WIDTH_fnc(self) -> int:
        return self.resolution[0] // 2

    def HALF_HEIGHT_fnc(self) -> int:
        return self.resolution[1] // 2

    def MOUSE_BORDER_RIGHT_fnc(self) -> int:
        return self.resolution[0] - self.MOUSE_BORDER_LEFT

    def NUM_RAYS_fnc(self) -> int:
        return self.HALF_WIDTH_fnc()

    def HALF_NUM_RAYS_fnc(self) -> int:
        return self.NUM_RAYS_fnc() // 2

    def DELTA_ANGLE_fnc(self):
        return self.FOV / self.NUM_RAYS_fnc()

    def SCREEN_DIST_fnc(self):
        return self.HALF_WIDTH_fnc() / math.tan(self.HALF_FOV)

    def SCALE_fnc(self) -> int:
        return self.resolution[0] // self.NUM_RAYS_fnc()

    def _prepare_static_vals(self):
        self.HALF_WIDTH = self.HALF_WIDTH_fnc()
        self.HALF_HEIGHT = self.HALF_HEIGHT_fnc()
        self.MOUSE_BORDER_RIGHT = self.MOUSE_BORDER_RIGHT_fnc()
        self.NUM_RAYS = self.NUM_RAYS_fnc()
        self.HALF_NUM_RAYS = self.HALF_NUM_RAYS_fnc()
        self.DELTA_ANGLE = self.DELTA_ANGLE_fnc()
        self.SCREEN_DIST = self.SCREEN_DIST_fnc()
        self.SCALE = self.SCALE_fnc()


class _SettingsDialog(QDialog, _help_dialog):

    def __init__(self, fpath: pl.Path = pl.Path(os.getenv('LOCALAPPDATA')) / 'PyQt_DOOM' / 'settings.json',
                 parent=None):
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setupUi(self)

        self.setWindowTitle("Settings")

        self.settings = GameSettings(fpath)

        self._prepare_gui()

        self.pushButton_music.clicked.connect(self._test_sound_music)
        self.pushButton_enemies.clicked.connect(self._test_sound_enemies)
        self.pushButton_player.clicked.connect(self._test_sound_player)
        self.pushButton_weapon.clicked.connect(self._test_sound_weapon)

        self.horizontalSlider_master.valueChanged.connect(lambda x: self.label_master.setText(str(x)))
        self.horizontalSlider_music.valueChanged.connect(lambda x: self.label_music.setText(str(x)))
        self.horizontalSlider_weapon.valueChanged.connect(lambda x: self.label_weapon.setText(str(x)))
        self.horizontalSlider_player.valueChanged.connect(lambda x: self.label_player.setText(str(x)))
        self.horizontalSlider_enemies.valueChanged.connect(lambda x: self.label_enemies.setText(str(x)))

        self.pushButton_use.clicked.connect(self._ok_clicked)
        self.pushButton_cancel.clicked.connect(self._cancel_clicked)

        self.tabWidget.setCurrentIndex(0)

        self._fill_gui()

    def _prepare_gui(self):
        self.comboBox_resolution.clear()
        res_texts = [f"{res[0]}x{res[1]}" for res in _resolutions]
        self.comboBox_resolution.addItems(res_texts)

        self.comboBox_fps_limit.clear()
        self.comboBox_fps_limit.addItems(list(_fps_limits.keys()))

    def _fill_gui(self):
        self.checkBox_original.setChecked(self.settings.original_pack)

        self.horizontalSlider_master.setValue(int(self.settings.volume_master * 100))
        self.horizontalSlider_music.setValue(int(self.settings.volume_music * 100))
        self.horizontalSlider_weapon.setValue(int(self.settings.volume_weapon * 100))
        self.horizontalSlider_player.setValue(int(self.settings.volume_player * 100))
        self.horizontalSlider_enemies.setValue(int(self.settings.volume_enemies * 100))

        self.checkBox_fullscreen.setChecked(self.settings.fullscreen)
        res_text = f"{self.settings.resolution[0]}x{self.settings.resolution[1]}"
        self.comboBox_resolution.setCurrentText(res_text)
        for fps_option in _fps_limits:
            if self.settings.fps_limit == _fps_limits[fps_option]:
                self.comboBox_fps_limit.setCurrentText(fps_option)
                break
        else:
            raise ValueError

    def _test_sound_music(self):
        self._update_settings()
        sound = Sound(None, self.settings)
        pg.mixer.music.play()
        sleep(4)
        pg.mixer.music.stop()

    def _test_sound_enemies(self):
        self._update_settings()
        sound = Sound(None, self.settings)
        sound_this = random.choice([sound.npc_pain, sound.npc_pain2, sound.npc_death, sound.npc_shot])
        sound_this.play()

    def _test_sound_player(self):
        self._update_settings()
        sound = Sound(None, self.settings)
        sound.player_pain.play()

    def _test_sound_weapon(self):
        self._update_settings()
        sound = Sound(None, self.settings)
        sound.shotgun.play()

    @staticmethod
    def getSliderValue(slider) -> float:
        return slider.value() / 100.0

    def getSelectedScreenResolution(self) -> (int, int):
        text = self.comboBox_resolution.currentText()
        return tuple([int(a) for a in text.split('x')])

    def getSelectedFPSLimit(self) -> int:
        text = self.comboBox_fps_limit.currentText()
        return _fps_limits[text]

    def _update_settings(self):
        self.settings.original_pack = self.checkBox_original.isChecked()

        self.settings.volume_master = self.getSliderValue(self.horizontalSlider_master)
        self.settings.volume_enemies = self.getSliderValue(self.horizontalSlider_enemies)
        self.settings.volume_weapon = self.getSliderValue(self.horizontalSlider_weapon)
        self.settings.volume_player = self.getSliderValue(self.horizontalSlider_player)
        self.settings.volume_music = self.getSliderValue(self.horizontalSlider_music)

        self.settings.fullscreen = self.checkBox_fullscreen.isChecked()
        self.settings.resolution = self.getSelectedScreenResolution()
        self.settings.fps_limit = self.getSelectedFPSLimit()

    def _ok_clicked(self):
        self._update_settings()

        self.settings.save()
        self.accept()

    def _cancel_clicked(self):
        self.accept()


def open_settings(parent):
    dialog = _SettingsDialog(parent=parent)
    dialog.exec_()
