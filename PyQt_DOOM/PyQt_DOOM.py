import pathlib as pl
import pygame as pg
import sys
import json
from loguru import logger
from datetime import datetime

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableWidgetItem

from PyQt_DOOM.settings import RES, FPS
from PyQt_DOOM.map import Map
from PyQt_DOOM.player import Player
from PyQt_DOOM.raycasting import RayCasting
from PyQt_DOOM.object_renderer import ObjectRenderer
from PyQt_DOOM.object_handler import ObjectHandler
from PyQt_DOOM.weapon import Weapon
from PyQt_DOOM.sound import Sound
from PyQt_DOOM.pathfinding import PathFinding


def save_json(data: dict, path: str | pl.Path) -> None:
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)


def load_json(path: str | pl.Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    return data


class SingleScore:
    def __init__(self, a: pl.Path | int = 0, kill_list=[], name=None, folder=pl.Path(__file__).parent / 'scores'):
        """
        :param a:           score (int) or path to existing score file
        :param kill_list:   list of killed enemies (strings)
        :param name:        custom score name
        :param folder:
        """
        if isinstance(a, pl.Path):
            the_dict = load_json(a)
            self.name = the_dict['name']
            self.score = the_dict['score']
            self.kill_list = the_dict['kill_list']
            self.fpath = a
        else:
            assert folder.is_dir()
            self.score = a
            self.kill_list = kill_list
            self.name = name
            self.folder = folder
            self.fpath = None

    def save(self):
        cur_time = str(datetime.now()).replace('-', '').replace(' ', '').replace('.', '').replace(':', '')
        if self.name in [None, '']:
            self.name = cur_time
        the_dict = {
            'name': self.name,
            'score': self.score,
            'kill_list': self.kill_list,
        }
        fpath = self.folder / f'{cur_time}.json'
        save_json(the_dict, fpath)
        self.fpath = fpath


class AllScores:
    def __init__(self, folder=pl.Path(__file__).parent / 'scores'):
        assert folder.is_dir()

        self._all = []
        from os import walk
        files = next(walk(folder), (None, None, []))[2]
        for file in files:
            fpath = folder / file
            score = SingleScore(fpath)
            self._all.append(score)

    def list(self) -> list[str]:
        if not len(self._all):
            return []

        names = []
        for score in self._all:
            if score.name in names:
                raise RuntimeError
            names.append(score.name)
        return names

    def _score_exists(self, name: str) -> bool:
        for score in self._all:
            if score.name == name:
                return True
        return False

    def get(self, name: str) -> SingleScore:
        if not self._score_exists(name):
            raise FileNotFoundError
        for score in self._all:
            if score.name == name:
                return score
        raise FileNotFoundError

    def add(self, score: SingleScore) -> None:
        if score.name in self.list():
            logger.error("This score already exists")
            raise RuntimeError

        self._all.append(score)

    def best_score(self) -> int:
        best = 0
        for score in self._all:
            best = max(best, score.score)
        return best

    def sorted(self):
        sorted_list = sorted(self._all, key=lambda x: x.score, reverse=True)
        return sorted_list


class Game:
    def __init__(self, score_plus, score_reset, finished_fnc):
        pg.init()
        pg.mouse.set_visible(False)
        self.score_plus = score_plus
        self.score_reset = score_reset
        self.finished_fnc = finished_fnc
        self.map = None
        self.player = None
        self.object_renderer = None
        self.object_handler = None
        self.raycasting = None
        self.weapon = None
        self.sound = None
        self.pathfinding = None
        self.screen = pg.display.set_mode(RES)
        pg.event.set_grab(True)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.new_game()

    def new_game(self):
        self.score_reset()
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        pg.mixer.music.play(-1)

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()
        # self.map.draw()
        # self.player.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.display.quit()
            elif event.type == self.global_event:
                self.global_trigger = True
            self.player.single_fire_event(event)

    def run(self):
        while True:
            try:
                self.check_events()
                self.update()
                self.draw()
            except Exception as e:
                logger.debug(e)
                logger.info("Game terminated")
                pg.mixer.quit()
                pg.quit()
                break


def start_doom(finished_fnc, score_reset, score_plus):
    score_reset()
    game = Game(score_plus, score_reset, finished_fnc)
    game.run()
    finished_fnc()


class MainModule:
    def __init__(self, widget) -> None:
        self.widget = widget
        self.widget.pushButton_play.clicked.connect(lambda: start_doom(self._game_finished, self._score_reset, self._score_plus))

        self.all_scores = AllScores()

        self.score = 0
        self.kill_list = []

        self._update_gui()

    def _game_finished(self):
        logger.info("Game finished")
        all_names = self.all_scores.list()
        new_name = 'Game 1'
        i = 1
        while new_name in all_names:
            i += 1
            new_name = f"Game {i}"
        score = SingleScore(a=self.score, kill_list=self.kill_list, name=new_name)
        score.save()
        self.all_scores.add(score)

        self._update_gui()

    def _score_plus(self, enemy_type=''):
        match enemy_type:
            case 'Soldier':
                score_plus = 2
            case 'Cyber Demon':
                score_plus = 7
            case 'Caco Demon':
                score_plus = 3
            case 'Level Finished':
                score_plus = 10
            case _:
                logger.error("You have killed some rare, unknown enemy, congrats :)")
                raise RuntimeError
        self.score += score_plus
        self.widget.label_last_score.setText(str(self.score))
        self.kill_list.append(enemy_type)

    def _score_reset(self):
        self.score = 0
        self.kill_list = []
        self.widget.label_last_score.setText(str(self.score))

    def _update_gui(self):
        self.widget.tableWidget.setRowCount(0)

        best_score = self.all_scores.best_score()
        self.widget.label_best_score.setText(str(best_score))

        games_played = len(self.all_scores.list())
        self.widget.label_games_played.setText(str(games_played))

        sorted_list = self.all_scores.sorted()
        for score in sorted_list:
            row_position = self.widget.tableWidget.rowCount()
            gt = str(score.fpath.with_suffix('').name)
            game_time_text = f"{gt[:4]} {gt[4:6]} {gt[6:8]} - {gt[8:10]}:{gt[10:12]}"
            self.widget.tableWidget.insertRow(row_position)
            self.widget.tableWidget.setItem(row_position, 0, QTableWidgetItem(f"{score.score}"))
            self.widget.tableWidget.setItem(row_position, 1, QTableWidgetItem(game_time_text))


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        window_path = pl.Path(__file__).parent / 'main_window.ui'
        uic.loadUi(window_path, self)
        self.setWindowTitle("PyQt DOOM")
        self.setWindowIcon(QtGui.QIcon(str(pl.Path(__file__).parent / 'data' / 'icon.ico')))
        self.widget_plugin = QWidget()
        widget_path = pl.Path(__file__).parent / 'pyqt_doom.ui'
        uic.loadUi(widget_path, self.widget_plugin)
        module = MainModule(widget=self.widget_plugin)
        self.stackedWidget.addWidget(self.widget_plugin)
        self.show()


def start():
    app = QtWidgets.QApplication(sys.argv)
    form = Main()
    form.show()
    app.exec_()


if __name__ == '__main__':
    start()
