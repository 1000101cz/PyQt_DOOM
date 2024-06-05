from time import sleep
import pathlib as pl
import pygame as pg
import random
import json

from loguru import logger
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from PyQt_DOOM.sound import Sound


_help_path = pl.Path(__file__).parent / 'settings.ui'
_help_dialog = uic.loadUiType(_help_path)[0]


def save_json(data: dict, path: str | pl.Path) -> None:
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def load_json(path: str | pl.Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    return data


class GameSettings:
    def __init__(self, fpath: pl.Path = pl.Path(__file__).parent.parent.parent / 'user_settings' / 'settings.json'):
        self.original_pack = False

        self.volume_master = 1.0
        self.volume_music = 1.0
        self.volume_enemies = 1.0
        self.volume_player = 1.0
        self.volume_weapon = 1.0

        if fpath.is_file():
            self.load(fpath)
        else:
            self.save(fpath)

    def get_dict(self):
        return {
                'original_pack': self.original_pack,

                'volume_master': self.volume_master,
                'volume_music': self.volume_music,
                'volume_enemies': self.volume_enemies,
                'volume_player': self.volume_player,
                'volume_weapon': self.volume_weapon
            }

    def save(self, fpath: pl.Path = pl.Path(__file__).parent.parent.parent / 'user_settings' / 'settings.json'):
        the_dict = self.get_dict()
        save_json(the_dict, fpath)

    def load(self, fpath: pl.Path = pl.Path(__file__).parent.parent.parent / 'user_settings' / 'settings.json'):
        the_dict = load_json(fpath)
        self.original_pack = the_dict['original_pack']

        self.volume_master = the_dict['volume_master']
        self.volume_music = the_dict['volume_music']
        self.volume_enemies = the_dict['volume_enemies']
        self.volume_player = the_dict['volume_player']
        self.volume_weapon = the_dict['volume_weapon']


class _SettingsDialog(QDialog, _help_dialog):

    def __init__(self, fpath: pl.Path = pl.Path(__file__).parent.parent.parent / 'user_settings' / 'settings.json',
                 parent=None):
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setupUi(self)

        self.setWindowTitle("Settings")

        self.settings = GameSettings(fpath)

        self._fill_gui()

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

    def _fill_gui(self):
        self.checkBox_original.setChecked(self.settings.original_pack)

        self.horizontalSlider_master.setValue(int(self.settings.volume_master * 100))
        self.horizontalSlider_music.setValue(int(self.settings.volume_music * 100))
        self.horizontalSlider_weapon.setValue(int(self.settings.volume_weapon * 100))
        self.horizontalSlider_player.setValue(int(self.settings.volume_player * 100))
        self.horizontalSlider_enemies.setValue(int(self.settings.volume_enemies * 100))

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

    def _update_settings(self):
        self.settings.original_pack = self.checkBox_original.isChecked()

        self.settings.volume_master = self.getSliderValue(self.horizontalSlider_master)
        self.settings.volume_enemies = self.getSliderValue(self.horizontalSlider_enemies)
        self.settings.volume_weapon = self.getSliderValue(self.horizontalSlider_weapon)
        self.settings.volume_player = self.getSliderValue(self.horizontalSlider_player)
        self.settings.volume_music = self.getSliderValue(self.horizontalSlider_music)

    def _ok_clicked(self):
        self._update_settings()

        self.settings.save()
        self.accept()

    def _cancel_clicked(self):
        self.accept()


def open_settings(parent):
    dialog = _SettingsDialog(parent=parent)
    dialog.exec_()
