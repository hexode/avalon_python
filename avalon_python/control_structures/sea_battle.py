#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
# battleship
# @description classic implementation of battleship game
# @author hexode <usr.noid@gmail.com>
#


'''
Warship tiles
    o     - single warship
    ++    - double warship
    @@@   - triple warship
    ####  - quadruple warship

    x     - breach in compartment
    .     - miss

Batlefield:

              <<<YOUR>>>                 ENEMY

              ABCDEFGHIJ              ABCDEFGHIJ
             +----------+            +----------+
@@@         1|@@@  0    |           1|   .      |
            2|       #  |           2|     .    |
            3|0      x  |           3| .  .     |
            4|   ++  #  |           4| .x.      |
            5|       #  |           5| .x.      |
            6|@@@       |           6| . .      |
            7|          |           7|          |
            8|    +  ++ |           8|     0    |
            9|0   +     |           9|          |
           10|        0 |          10|  .       |
             +----------+            +----------+

'''
'''
TODO:
    use curses.rectangle for draw battlefield borders
'''

import sys
import time
import curses
from curses.textpad import Textbox
import itertools
from enum import Enum
from sig import Signal


class Tile():
    CORVETTE = 'o'
    FRIGATE = '+'
    DESTROYER = '@'
    BATTLECRUISER = '#'
    MISS = '.'
    EMPTY_SECTOR = ' '
    HIT = 'x'


class Screen():
    def __init__(self, max_x, max_y, stdscr):
        self.max_x = max_x
        self.max_y = max_y
        self.stdscr = stdscr

    def set_char(self, x, y, char):
        self.stdscr.addstr(y, x, char[0])

    def set_str(self, x, y, string):
        self.stdscr.addstr(y, x, string)

    def render(self):
        self.stdscr.refresh()


class Warship():
    warship_types = Enum([
        'CORVETTE',
        'FRIGATE',
        'DESTROYER',
        'BATTLECRUISER'
    ], xrange)

    hull_state = Enum([
        'NORMAL',
        'DAMAGED',
        'DESTROYED',
    ], xrange)

    compartment_state = Enum([
        'NORMAL',
        'DESTROYED',
    ], xrange)

    collision_status = Enum([
        'HIT',
        'ALREADY_HIT',
        'DESTROYED',
        'MISS',
    ], xrange)

    warship_param_list = [
        {'_type': warship_types.CORVETTE, 'tile': Tile.CORVETTE, 'length': 1},
        {'_type': warship_types.FRIGATE, 'tile': Tile.FRIGATE, 'length': 2},
        {'_type': warship_types.DESTROYER, 'tile': Tile.DESTROYER, 'length': 3},
        {'_type': warship_types.BATTLECRUISER, 'tile': Tile.BATTLECRUISER, 'length': 4},
    ]

    def __init__(self, x1, y1, x2, y2):
        coord = locals().copy()
        del coord['self']
        warship_type = Warship.determine_type(**coord)

        if warship_type not in Warship.warship_types:
            raise Exception('Unknown warship type')

        self.coord = coord
        self._type = warship_type
        self.params = self.warship_param_list[warship_type]
        self.compartments = self.build_compartments(**coord)

        # Оповещения о повреждениях
        self.no_damage = Signal()
        self.hit = Signal()
        self.already_hit = Signal()
        self.destroyed = Signal()

    @staticmethod
    def determine_type(x1, y1, x2, y2):
        '''
        Определяем по координатам тип корабля
        '''
        length = Warship.determine_length(**locals())
        if not length:
            raise Exception('Wrong coordinates warship')
        if not (0 < length < 5):
            raise Exception('Wrong length of warship')

        warship_params = filter(lambda pl: pl['length'] == length, Warship.warship_param_list)[0]
        return warship_params['_type']

    @staticmethod
    def determine_length(x1, y1, x2, y2):
        '''
        Определяем длину корабля
        1..4 допустимая длина
        None - если корабль не лежить вертикально или горизонтально
        '''
        if not (x2 - x1 == 0 or y2 - y1 == 0):
            return None
        return (abs(x2 - x1) or abs(y2 - y1)) + 1

    # FIXME: Кажется, что этот метод можно упростить
    @staticmethod
    def build_compartments(x1, y1, x2, y2):
        '''
        Генерируем отсеки:
        формат: (x, y, целостность_отсека=1)
        целостность 1 - целый, 0 - имеются повреждения
        '''
        if x2 == x1:
            low, high = sorted([y1, y2])
            high += 1
            x = x1
            compartments = [[x, y, Warship.compartment_state.NORMAL] for y in xrange(low, high)]
        else:
            low, high = sorted([x1, x2])
            high += 1
            y = y1
            compartments = [[x, y, Warship.compartment_state.NORMAL] for x in xrange(low, high)]

        return compartments

    @staticmethod
    def check_hull_condition(compartments):
        ''' Проверка целостности корпуса'''
        condition = [c[2] for c in compartments]

        if all(condition):
            return Warship.hull_state.NORMAL
        elif any(condition):
            return Warship.hull_state.DAMAGED
        else:
            return Warship.hull_state.DESTROYED

    @staticmethod
    def collide(compartments, x, y):
        ''' Расчет столкновения с отсеком '''
        for compartment in compartments:
            comp_x, comp_y, comp_cond = compartment

            if comp_x == x and comp_y == y:
                if comp_cond == Warship.compartment_state.NORMAL:
                    # помечаем отсек как разрушенный
                    compartment[-1] = Warship.compartment_state.DESTROYED

                    if Warship.check_hull_condition(compartments) == Warship.hull_state.DAMAGED:
                        return Warship.collision_status.HIT
                    else:
                        return Warship.collision_status.DESTROYED
                # Данный отсек уже разрушен
                else:
                    return Warship.collision_status.ALREADY_HIT
        return Warship.collision_status.MISS

    def get_compartments(self):
        return self.compartments

    def take_fire(self, x, y):
        collision = Warship.collide(self.get_compartments(), x, y)

        if collision == Warship.collision_status.HIT:
            self.already_hit.fire(self)
        elif collision == Warship.collision_status.MISS:
            self.no_damage.fire(self)
        else:
            self.already_hit.fire(self)


class Fleet():
    fleet = []

    fleet_state = Enum([
        'NORMAL',
        'HAS_LOSSES',
        'DEFEAT',
    ], xrange)

    def __init__(self):
        # Оповещение о выстреле
        self.shot = Signal()
        # Оповещение о попадании
        self.hit = Signal()
        # Изменилась обстановка
        self.change = Signal()

    def take_under_command(self, warship):
        # Передаем кораблю удар по расположению флотилии
        self.hit.connect(warship.take_fire)

        # Реагируем на сигналы от боевых кораблей
        warship.no_damage.connect(self.on_warship_no_damage)
        warship.hit.connect(self.on_warship_hit)
        warship.already_hit.connect(self.on_warship_already_hit)
        warship.destroyed.connect(self.on_warship_destroyed)

        self.fleet.append(warship)

        self.change.fire()

    def get_fleet(self):
        return self.fleet

    def on_warship_hit(self):
        self.change.fire()

    def on_warship_already_hit(self):
        self.change.fire()

    def on_warship_no_damage(self):
        self.change.fire()

    def on_warship_destroyed(self):
        self.change.fire()

    @staticmethod
    def get_damage_report(fleet):
        return [warship.check_hull_condition() for warship in fleet]

    @staticmethod
    def get_fleet_state():
        damage_report = Fleet.get_damage_report()

        def check(value):
            def _check(c):
                return c == value
            return _check

        intact_warships_count = len(filter(check(Warship.hull_state.NORMAL), damage_report))
        damaged_warships_count = len(filter(check(Warship.hull_state.DAMAGED), damage_report))
        destroyed_warships_count = len(filter(check(Warship.hull_state.DESTROYED), damage_report))

        if intact_warships_count == len(damage_report):
            return Warship.fleet_state.NORMAL
        elif destroyed_warships_count < len(damage_report) or damaged_warships_count > 0:
            return Warship.fleet_state.HAS_LOSSES
        else:
            return Warship.fleet_state.DEFEAT

    def shoot(self, x, y):
        self.shot.fire(x, y)

    def take_fire(self, x, y):
        self.hit.fire(x, y)


class Battlefield():

    def __init__(self, fleet, is_enemy=False):
        self.battlefield = [[False for i in range(10)] for i in range(10)]
        self.fleet = fleet
        self.pad = curses.newpad(14, 14)
        self.is_enemy = is_enemy

        fleet.change.connect(self.render)
        # переносим выстрелы по флотилии на карту боя
        fleet.hit.connect(self.update_battlefield)

    def draw_border(self, x, y, width, height):
        ''' Отрисовка рамки поля '''
        CORNER = '+'
        HOR = '-'
        VER = '|'

        self.pad.addstr(y, x + 1, HOR * (width - 2))
        self.pad.addstr(y + height - 1, x + 1, HOR * (width - 2))

        for i in range(1, height - 1):
            self.pad.addstr(y + i, x, VER)
            self.pad.addstr(y + i, x + width - 1, VER)

        self.pad.addstr(y, x, CORNER)
        self.pad.addstr(y, x + width - 1, CORNER)
        self.pad.addstr(y + height - 1, x, CORNER)
        self.pad.addstr(y + height - 1, x + width - 1, CORNER)

    def draw_coord_scale(self, x, y):
        ''' отрисовка шкалы '''
        letter_scale = ''.join([chr(i) for i in xrange(ord('A'), ord('A') + 10)])
        self.pad.addstr(y, x + 2, letter_scale)

        digit_scale = itertools.count(1, 1)
        for i in range(2, 11):
            self.pad.addstr(y + i, x, str(digit_scale.next()))

        # рисуем 10 со сдвигом влево
        self.pad.addstr(y + 11, x - 1, str(digit_scale.next()))

    def render(self, offset_x=1, offset_y=1):
        ''' Отрисовка поля боя '''
        tiles = [Tile.EMPTY_SECTOR, Tile.MISS]

        # Рисуем поле боя без учета флотилии
        for y, sector_line in enumerate(self.battlefield):
            for x, sector in enumerate(sector_line):
                self.pad.addstr(y, x, tiles[sector])

        self.draw_border(2, 1, 12, 12)
        self.draw_coord_scale(1, 0)

        # Если это поле боя игрока, то рисуем его флотилию
        if not self.is_enemy:
            for warship in self.fleet.get_fleet():
                warship_tile = warship.params['tile']
                for compartment in warship.get_compartments():
                    x, y, compartment_condition = compartment
                    if compartment_condition == Warship.compartment_state.DESTROYED:
                        compartment_tile = Tile.HIT
                    else:
                        compartment_tile = warship_tile
                    self.pad.addstr(y + 2, x + 3, compartment_tile)

        self.pad.refresh(0, 0, offset_y, offset_x, offset_y + 13, offset_x + 13)

    def update_battlefield(self, x, y):
        self.battlefield[x][y] = True


class Game():
    def __init__(self, screen):
        self.screen = screen

    @staticmethod
    def show_intro(screen):
        title = r'''
 ______  _______ _______ _______        _______ _______ _     _ _____  _____
 |_____] |_____|    |       |    |      |______ |______ |_____|   |   |_____]
 |_____] |     |    |       |    |_____ |______ ______| |     | __|__ |
'''
        warship = r'''
                                     |__
                                     |\/
                                     ---
                                     / | [
                              !      | |||
                            _/|     _/|-++'
                        +  +--|    |--|--|_ |-
                     { /|__|  |/\__|  |--- |||__/
                    +---------------___[}-_===_.'____                 /\
                ____`-' ||___-{]_| _[}-  |     |_[___\==--            \/   _
 __..._____--==/___]_|__|_____________________________[___\==--____,------' .7
|  o                                                                       /
 \_________________________________________________________________________|

'''
        menu = '\n'.join([
            r'n - new game',
            r'q - quit game'
        ])

        def draw_text_center(text, offset_y):
            height, width = screen.stdscr.getmaxyx()
            text_width = max([len(line) for line in text.split('\n')])
            text_height = len(text.split('\n'))
            offset_x = height - text_width / 2

            for line_ix, line in enumerate(text.split('\n')):
                screen.set_str(offset_x, offset_y + line_ix, line)

            return text_height + offset_y

        offset_y = draw_text_center(title, 0)
        offset_y = draw_text_center(warship, offset_y + 1)
        draw_text_center(menu, offset_y + 1)
        key = screen.stdscr.getch()

        if key == ord('q'):
            sys.exit()
        if key == ord('n'):
            return Game(screen)

    def define_fleet_order(self, is_player):
        stdscr = self.screen.stdscr

        height, width = stdscr.getmaxyx()
        fleet = Fleet()
        battlefield = Battlefield(fleet)
        battlefield.render()

        while True:
            warship_coord = None  # box.gather()
            if warship_coord:
                continue
            else:
                pass

        '''
        while fleet.is_staffed():
        '''


class QAREPL():
    def __init__(self, stdscr):
        self.history = []
        self.stdscr = stdscr

    def save_to_history(self, msg):
        self.history.append(msg)
        if len(self.history) > self.height:
            self.history = self.history[1:]

    def setup(self, x, y, width, height):
        self.prompt_params = y + height - 1, x
        self.input_params = y + height, x
        self.width = width
        self.x, self.y = x, y

    def enable(self):
        self.editwin = curses.newwin(1, self.width, self.height - 2, self.x)
        self.box = Textbox(self.editwin)

    def disable(self):
        self.editwin.clear()
        self.editwin = None
        self.box = None

    def ask(self, prompt, right, wrong, validator):
        self.editwin.clear()
        prompt_args = self.prompt_params.append + (prompt,)
        self.stdscr.addstr(*prompt_args)
        while True:
            self.box.edit()
            user_input = self.box.gather()
            if validator(user_input):
                self.save_to_history(prompt)
                self.save_to_history(user_input)
            else:
                pass


def tick(screen):
    screen.stdscr.clear()
    screen.render()


def main(stdscr):
    SCREEN_WIDTH = 10
    SCREEN_HEIGHT = 10

    FPS = 10

    FRAME_DURATION = 1000.0 / FPS

    # curses.curs_set(0) # отключение курсора
    stdscr.border(0)

    screen = Screen(SCREEN_WIDTH, SCREEN_HEIGHT, stdscr)

    game = Game.show_intro(screen)
    stdscr.clear()
    stdscr.border(0)
    stdscr.refresh()

    player_fleet = game.define_fleet_order(is_player=True)
    player_fleet.take_fire(10, 10)

    # GAME LOGIC
    # scene.player_battle_fleet = Fleet()
    # # TODO может переместить создание окна в Battlefield
    # scene.player_battlefield = BattleField(scene.player_battle_fleet, battlefield_pad)

    # perframe cycle
    while True:
        t1 = time.clock()
        tick(screen)
        delta = time.clock() - t1
        downtime = FRAME_DURATION - delta

        # Ждем до конца кадра
        time.sleep(0 if downtime < 0 else downtime / 1000)

if __name__ == '__main__':
    curses.wrapper(main)
