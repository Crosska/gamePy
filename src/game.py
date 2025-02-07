import random

from core import GameAPI
from constants import Sprite, GRID_SIZE
from PyQt5.QtGui import QVector2D
from shipData import ShipData


class Island:
    def __init__(self, x, y, obstacle_type):
        # Инициализация острова
        self.position = QVector2D(x, y)
        self.obstacle_type = obstacle_type
        self.image = Sprite.CLIFF if obstacle_type else Sprite.ISLAND

    def place(self, api: GameAPI):
        # Создает изображение острова на поле
        api.addImage(self.image, self.position.x(), self.position.y())


class Ship:
    def __init__(self, x, y, ship_data, team):
        self.position = QVector2D(x, y)
        self.damage, self.health, self.speed, self.name = ship_data
        self.team = team
        self.selected = False
        self.image_obj = None

        if team == "green":
            if ship_data == ShipData.ENG_DESTROYER:
                self.image = Sprite.GREEN_DESTROYER
            elif ship_data == ShipData.ENG_CRUISER:
                self.image = Sprite.GREEN_CRUISER
            elif ship_data == ShipData.ENG_BATTLESHIP:
                self.image = Sprite.GREEN_BATTLESHIP
        else:
            if ship_data == ShipData.GER_DESTROYER:
                self.image = Sprite.RED_DESTROYER
            elif ship_data == ShipData.GER_CRUISER:
                self.image = Sprite.RED_CRUISER
            elif ship_data == ShipData.GER_BATTLESHIP:
                self.image = Sprite.RED_BATTLESHIP

    def place(self, api: GameAPI):
        self.image_obj = api.addImage(self.image, self.position.x(), self.position.y())

    def toggle_selection(self, api: GameAPI):

        self.selected = not self.selected
        if self.selected:
            self.image_obj = api.addImage(Sprite.SELECTION, self.position.x(), self.position.y())
            self.image_obj.show()
            api.addMessage(f"{self.name} selected")
        else:
            self.image_obj.hide()
            self.image_obj = api.addImage(self.image, self.position.x(), self.position.y())
            api.addMessage(f"{self.name} deselected")


class Game(object):
    global move

    def __init__(self):
        # Инициализация игры
        self.api = None
        self.islands = []
        self.green_ships = []
        self.red_ships = []
        self.move = False
        self.selected_ship = None

    def start(self, api: GameAPI) -> None:
        api.addMessage('--- GREEN TEAM MOVE ---')

        # Расстановка препятствий
        occupied_positions = set()
        island_count = random.randint(1, 15)

        while len(self.islands) < island_count:
            x, y = random.randint(1, GRID_SIZE - 2), random.randint(0, GRID_SIZE - 1)
            if (x, y) not in occupied_positions:
                obstacle_type = random.choice([True, False])
                island = Island(x, y, obstacle_type)
                island.place(api)
                self.islands.append(island)
                occupied_positions.add((x, y))

        # Расстановка кораблей
        self.place_ships(api, "green", 0, occupied_positions,
                         [ShipData.ENG_DESTROYER, ShipData.ENG_CRUISER, ShipData.ENG_BATTLESHIP])
        self.place_ships(api, "red", GRID_SIZE - 1, occupied_positions,
                         [ShipData.GER_DESTROYER, ShipData.GER_CRUISER, ShipData.GER_BATTLESHIP])

    def place_ships(self, api: GameAPI, team, row, occupied_positions, ship_data_list):
        for i, ship_data in enumerate(ship_data_list):
            y, x = i * 2, row
            ship = 'null'
            if (x, y) not in occupied_positions:
                ship = Ship(x, y, ship_data, team)
                ship.place(api)
                occupied_positions.add((x, y))
            if team == "green":
                self.green_ships.append(ship)
            else:
                self.red_ships.append(ship)

    def click(self, api: GameAPI, x: int, y: int) -> None:
        api.addMessage('click {}, {}'.format(x, y))
        ship_obj: Ship = None
        island_found = False

        for island in self.islands:
            if int(island.position.x()) == x and int(island.position.y()) == y:
                island_found = True
                break

        if self.move:
            for ship in self.green_ships:
                if int(ship.position.x()) == x and int(ship.position.y()) == y:
                    ship_obj = ship
                    break
        else:
            for ship in self.red_ships:
                if int(ship.position.x()) == x and int(ship.position.y()) == y:
                    ship_obj = ship
                    break

        if island_found:
            api.addMessage('This is an obstacle')
        else:
            if ship_obj is not None:
                if self.selected_ship == ship_obj:
                    ship_obj.toggle_selection(api)
                    self.selected_ship = None
                else:
                    if self.selected_ship:
                        self.selected_ship.toggle_selection(api)
                    ship_obj.toggle_selection(api)
                    self.selected_ship = ship_obj
            else:
                api.addMessage("This is an empty cell")
