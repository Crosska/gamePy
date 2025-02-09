import math
import random

from core import GameAPI
from constants import Sprite, GRID_SIZE
from PyQt5.QtGui import QVector2D
from shipData import ShipData

# Класс Island описывающий остров-препятствие и его поведение
class Island:

    # Инициализация препятствия-острова
    def __init__(self, x, y, obstacle_type):
        self.position = QVector2D(x, y)
        self.obstacle_type = obstacle_type
        self.image = Sprite.CLIFF if obstacle_type else Sprite.ISLAND

    # Появление препятствия-острова
    def place(self, api: GameAPI):
        api.addImage(self.image, self.position.x(), self.position.y())

TEAM_SHIPS = {
    "green": {
        ShipData.ENG_DESTROYER: (Sprite.GREEN_DESTROYER, "Destroyer"),
        ShipData.ENG_CRUISER: (Sprite.GREEN_CRUISER, "Cruiser"),
        ShipData.ENG_BATTLESHIP: (Sprite.GREEN_BATTLESHIP, "Battleship"),
    },
    "red": {
        ShipData.GER_DESTROYER: (Sprite.RED_DESTROYER, "Destroyer"),
        ShipData.GER_CRUISER: (Sprite.RED_CRUISER, "Cruiser"),
        ShipData.GER_BATTLESHIP: (Sprite.RED_BATTLESHIP, "Battleship"),
    }
}

# Класс Ship описывающий корабль и его поведение
class Ship:

    # Инициализация корабля
    def __init__(self, x, y, ship_data, team):
        self.position = QVector2D(x, y)
        self.damage, self.health, self.speed, self.name = ship_data
        self.selected = False
        self.ship_marker_obj = None
        self.selection_image_obj = None
        self.image, self.ship_type = TEAM_SHIPS[team][ship_data]
        self.isAlive = True

        if team == "green":
            if ship_data == ShipData.ENG_DESTROYER:
                self.image = Sprite.GREEN_DESTROYER
                self.ship_type = 'Destroyer'
            elif ship_data == ShipData.ENG_CRUISER:
                self.image = Sprite.GREEN_CRUISER
                self.ship_type = 'Cruiser'
            elif ship_data == ShipData.ENG_BATTLESHIP:
                self.image = Sprite.GREEN_BATTLESHIP
                self.ship_type = 'Battleship'
        else:
            if ship_data == ShipData.GER_DESTROYER:
                self.image = Sprite.RED_DESTROYER
                self.ship_type = 'Destroyer'
            elif ship_data == ShipData.GER_CRUISER:
                self.image = Sprite.RED_CRUISER
                self.ship_type = 'Cruiser'
            elif ship_data == ShipData.GER_BATTLESHIP:
                self.image = Sprite.RED_BATTLESHIP
                self.ship_type = 'Battleship'

    # Атака корабля
    def attack(self, api: GameAPI, ships, big_obstacles):
        api.addMessage(f"\n{self.name} attacks")
        attacked_ships = []

        # Проверка попадание кораблей противника в радиус атаки
        if self.ship_type == 'Destroyer':
            for ship in ships:
                # Проверка на атаку вокруг себя по вертикали и горизонтали
                if ship.position.x() == (self.position.x() + 1) and ship.position.y() == self.position.y():
                    attacked_ships.append(ship)
                if ship.position.x() == (self.position.x() - 1) and ship.position.y() == self.position.y():
                    attacked_ships.append(ship)
                if ship.position.x() == self.position.x() and ship.position.y() == (self.position.y() + 1):
                    attacked_ships.append(ship)
                if ship.position.x() == self.position.x() and ship.position.y() == (self.position.y() - 1):
                    attacked_ships.append(ship)
        else:
            for ship in ships:
                # Проверка на атаку линиями по вертикали и горизонтали, с учетом больших островов (Cliff)
                if ship.position.x() == self.position.x():
                    min_y, max_y = sorted([int(self.position.y()), int(ship.position.y())])
                    if any((self.position.x(), y) in big_obstacles for y in range(min_y + 1, max_y)):
                        continue
                    attacked_ships.append(ship)
                elif ship.position.y() == self.position.y():
                    min_x, max_x = sorted([int(self.position.x()), int(ship.position.x())])
                    if any((x, self.position.y()) in big_obstacles for x in range(min_x + 1, max_x)):
                        continue
                    attacked_ships.append(ship)

        # Проверка на атаку корабля
        if len(attacked_ships) > 0:
            deal_damage = int(self.damage / len(attacked_ships))
            # api.addMessage(f"Ships attacked - {len(attacked_ships)} so damage is {int(deal_damage)}")
            for ship in attacked_ships:
                if ship.ship_type == 'Battleship':
                    if deal_damage > 10:
                        ship.take_damage(api, deal_damage, self.name)
                    else:
                        api.addMessage(f"All damage blocked by {ship.name} Battleship armor because damage <= 10")
                elif ship.ship_type == 'Cruiser' or ship.ship_type == 'Destroyer':
                    distance = abs(
                        ship.position.y() - self.position.y()) if ship.position.x() == self.position.x() else abs(
                        ship.position.x() - self.position.x())
                    if distance > 2:
                        api.addMessage(
                            f"Dealt damage reduced from {deal_damage} by / 2 because distance for {ship.name} {ship.ship_type} is {int(distance)}")
                        ship.take_damage(api, math.floor(deal_damage / 2), self.name)
                    else:
                        ship.take_damage(api, deal_damage, self.name)

    # Получение урона
    def take_damage(self, api: GameAPI, deal_damage, name):
        self.health = float(self.health) - float(deal_damage)
        self.update_marker()
        if self.health <= 0:
            self.destroy()
            api.addMessage(
                f"{self.name} on was fallen")
            return
        characters = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G'}
        api.addMessage(
            f"{name} deals {int(deal_damage)} damage to {self.name} on {characters[self.position.x()]}{int(self.position.y() + 1)}\n{self.name} current HP is {int(self.health)}")

    # Смерть корабля
    def destroy(self):
        self.ship_marker_obj.hide()
        self.isAlive = False

    # Появление на карте
    def place(self, api: GameAPI):
        self.ship_marker_obj = api.addMarker(self.image, self.position.x(), self.position.y())

    # Выбор корабля как активного
    def toggle_selection(self, api: GameAPI):
        self.selected = not self.selected
        if self.selected:
            self.ship_marker_obj.setSelected(True)
            # api.addMessage(f"{self.name} was selected")
        else:
            self.ship_marker_obj.setSelected(False)
            # api.addMessage(f"{self.name} was deselected")

    # Передвижение корабля
    def move(self, api: GameAPI, new_x, new_y, occupied_positions):
        distance = abs(self.position.x() - new_x) + abs(self.position.y() - new_y)

        # Расстояние перемещения больше чем скорость корабля
        if distance > self.speed:
            api.addMessage(f"Target cell too far, your speed is {self.speed}, distance is {int(distance)}")
            return False

        # Перемещение на занятую клетку
        if (new_x, new_y) in occupied_positions:
            api.addMessage("Target cell is occupied already")
            return False

        occupied_positions.remove((int(self.position.x()), int(self.position.y())))
        self.ship_marker_obj.hide()
        self.position = QVector2D(new_x, new_y)
        self.ship_marker_obj.moveTo(new_x, new_y)
        self.ship_marker_obj.show()
        occupied_positions.add((new_x, new_y))
        characters = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G'}
        api.addMessage(f"{self.name} moved to {characters[new_x]}{new_y + 1}")
        return True

    # Обновить индикатор здоровья
    def update_marker(self):
        self.ship_marker_obj.setHealth(self.health / 100)

# Класс Game описывающий игру и основное поведение
class Game(object):

    # Инициализация игры
    def __init__(self):
        self.api = None
        self.islands = []
        self.green_ships = []
        self.red_ships = []
        self.big_obstacles = set()
        self.move = True
        self.selected_ship = None
        self.occupied_positions = set()
        self.gameover = False

    # Начало игры
    def start(self, api: GameAPI) -> None:
        api.addMessage('!!! GAME STARTED !!!\n\n--- GREEN TEAM MOVE ---')
        island_count = random.randint(1, 15)

        # Цикл по размещению случайного количества островов-препятствий
        while len(self.islands) < island_count:
            x, y = random.randint(1, GRID_SIZE - 2), random.randint(0, GRID_SIZE - 1)
            if (x, y) not in self.occupied_positions:
                obstacle_type = random.choice([True, False])
                if obstacle_type:
                    self.big_obstacles.add((x, y))
                island = Island(x, y, obstacle_type)
                island.place(api)
                self.islands.append(island)
                self.occupied_positions.add((x, y))

        self.place_ships(api, "green", 0, [ShipData.ENG_DESTROYER, ShipData.ENG_CRUISER, ShipData.ENG_BATTLESHIP])
        self.place_ships(api, "red", GRID_SIZE - 1,
                         [ShipData.GER_DESTROYER, ShipData.GER_CRUISER, ShipData.GER_BATTLESHIP])

    # Первая расстановка кораблей
    def place_ships(self, api: GameAPI, team, row, ship_data_list):
        for i, ship_data in enumerate(ship_data_list):
            y, x = (i * 2) + 1, row
            if (x, y) not in self.occupied_positions:
                ship = Ship(x, y, ship_data, team)
                ship.place(api)
                self.occupied_positions.add((x, y))
                if team == "green":
                    self.green_ships.append(ship)
                else:
                    self.red_ships.append(ship)

    # Клик по клетке на карте
    def click(self, api: GameAPI, x: int, y: int) -> None:
        if not self.gameover:
            ship_obj = None
            island_found = False

            # Проверка на клик по острову
            for island in self.islands:
                if int(island.position.x()) == x and int(island.position.y()) == y:
                    island_found = True
                    break

            # Проверка на клик по кораблю
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

            # Проверка на что нажал игрок
            if island_found:
                api.addMessage('This is an obstacle')
            elif ship_obj is not None:
                if self.selected_ship == ship_obj:
                    ship_obj.toggle_selection(api)
                    self.selected_ship = None
                else:
                    if self.selected_ship:
                        self.selected_ship.toggle_selection(api)
                    ship_obj.toggle_selection(api)
                    self.selected_ship = ship_obj
            elif self.selected_ship is not None:
                is_moved = self.selected_ship.move(api, x, y, self.occupied_positions)
                if is_moved:
                    self.selected_ship.toggle_selection(api)

                    # Атака кораблей противника после успешного хода
                    for ship in (self.green_ships if not self.move else self.red_ships):
                        ship.attack(api, self.red_ships if not self.move else self.green_ships,
                                    self.big_obstacles)
                    game_status = self.check_dead_ships()

                    # Проверка на завершение игры
                    if game_status == 'Germany':
                        api.addMessage("\n\n!!! GERMANY (RED TEAM) WINS !!!\n\n")
                        self.gameover = True
                        return
                    elif game_status == 'England':
                        api.addMessage("\n\n!!! ENGLAND (GREEN TEAM) WINS !!!\n\n")
                        self.gameover = True
                        return

                    self.selected_ship = None
                    self.move = not self.move
                    api.addMessage('\n--- RED TEAM MOVE ---' if not self.move else '\n--- GREEN TEAM MOVE ---')
        else:
            api.addMessage("Game is over!")

    # Проверка кораблей для удаления потонувших
    def check_dead_ships(self):
        for ship in self.green_ships:
            if not ship.isAlive:
                self.occupied_positions.remove((ship.position.x(), ship.position.y()))
                self.green_ships.remove(ship)
                if len(self.green_ships) == 0:
                    return 'Germany'
        for ship in self.red_ships:
            if not ship.isAlive:
                self.occupied_positions.remove((ship.position.x(), ship.position.y()))
                self.red_ships.remove(ship)
                if len(self.red_ships) == 0:
                    return 'England'
        return 'Continue'