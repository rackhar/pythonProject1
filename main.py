from random import randint
from time import sleep


# Размер игровой доски
BOARD_SIZE = 6
# Длины / количество палуб всех кораблей в порядке убывания
SHIPS_TYPES = [3, 2, 2, 1, 1, 1, 1]


class BoardException(Exception):
    """
    Родительский класс для представления ошибок в игре.
    """

    pass


class BoardOutException(BoardException):
    """
    Класс для представления ошибки выстрела за пределы игровой доски.
    """

    def __str__(self) -> str:
        """
        Устанавливает выводимое сообщение об ошибке
        """

        return '\n\tЭта точка за пределами игрового поля!\n'


class BoardUsedException(BoardException):
    """
    Класс для представления ошибок выстрела в уже отстрелянную точку.
    """

    def __str__(self) -> str:
        """
        Устанавливает выводимое сообщение об ошибке
        """

        return '\n\tВы уже стреляли в эту точку!\n'


class BoardWrongShipException(BoardException):
    """
    Класс для представления ошибки размещения корабля.
    Эта ошибка нужна только для внутренней логики игры
    и не будет показываться пользователю.
    """

    pass


class Dot():
    """
    Класс для представления точки на доске.

    Атрибуты
    --------
    x : int
        Координата по оси x.
    y : int
        Координата по оси y.
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Устанавливает все необходимые атрибуты для объекта Dot.

        Атрибуты
        --------
        x : int
            Координата по оси x.
        y : int
            Координата по оси y.
        """

        self.x = x
        self.y = y

    def __eq__(self, other: 'Dot') -> bool:
        """
        Позволяет проверять точки на равенство.
        Теперь, чтобы проверить, находится ли точка в списке,
        достаточно просто использовать оператор in.
        """

        return self.x == other.x and self.y == other.y


class Ship():
    """
    Класс для представления корабля на доске.

    Атрибуты
    --------
    length : int
        Длина.
    bow : Dot
        Точка, где размещён нос корабля.
    direction : int
        Направление корабля (вертикальное/горизонтальное).
    lives : int
        Количеством жизней (сколько точек корабля еще не подбито).

    Методы
    --------
    @property
    dots():
        Возвращает список всех точек корабля.
    is_strike(Dot):
        Проверяет попадание,
        иными словами, принадлежит ли точка dot этому кораблю.
    """

    def __init__(self, length: int, bow: Dot, direction: int) -> None:
        """
        Устанавливает все необходимые атрибуты для объекта Ship.

        Атрибуты
        --------
        length : int
            Длина.
        bow : Dot
            Точка, где размещён нос корабля.
        direction : int
            Направление корабля (вертикальное/горизонтальное).
        lives : int
            Количеством жизней (сколько точек корабля еще не подбито).
        """

        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    @property
    def dots(self) -> list[Dot]:
        """
        Возвращает список всех точек корабля.
        """

        dot_list = list()
        for i in range(self.length):
            x, y = self.bow.x, self.bow.y

            if self.direction == 0:
                x += i
            elif self.direction == 1:
                y += i

            dot_list.append(Dot(x, y))
        return dot_list

    def is_strike(self, dot: Dot) -> bool:
        """
        Проверяет попадание,
        иными словами, принадлежит ли точка dot этому кораблю.
        """

        return dot in self.dots


class Board():
    """
    Класс для представления игровой доски.

    Атрибуты
    --------
    _is_hidden : bool
        Информация о том, нужно ли скрывать
        корабли на доске (для вывода доски соперника),
        или нет (для своей доски).
    table : list
        Двумерный список, в котором хранятся состояния каждой из клеток.
        При инициации заполняется символами моря '○'.
    ships : list
        Список кораблей доски.
    locked_dots : list
        Список заблокированных точек: во время генерации случайной доски
        служит для хранения уже занятых кораблями и их ореолами точек, а
        во время игры служит для хранения точек, куда игрок уже стрелял.
    live_ships : int
        Количество живых кораблей на доске.

    Методы
    --------
    @property
    def is_hidden():
        Геттер для параметра _is_hidden
    @is_hidden.setter
    def is_hidden():
        Сеттер для параметра _is_hidden
    add_ship(Ship):
        Ставит корабль на доску (если не получается, выбрасывает исключение).
    mark_oreol(Ship, is_game=True):
        Формирует ореол корабля, т.е. помечает точки вокруг,
        где другого корабля по правилам быть не может.
    show():
        Выводит доску в консоль в зависимости от параметра _is_hidden.
    @staticmethod
    out(Dot):
        Возвращает True , если точка выходит за пределы доски,
        и False, если не выходит.
    shot(Dot):
        Делает выстрел по доске.
        Если есть попытка выстрелить за пределы доски или
        в использованную точку, то выбрасывает исключения.
        Возвращает True, если право следующего хода остаётся за текущим игроком
        и False, если право следующего хода переходит сопернику.
    get_ready():
        Обнуляет перед стартом игры список заблокированных точек,
        который использовался во время генерации доски.
    is_loser():
        Проверяет состояние проигрыша.
    """

    _is_hidden: bool = False

    def __init__(self) -> None:
        """
        Устанавливает все необходимые атрибуты для объекта Board.

        Атрибуты
        --------
        table : list
            Двумерный список, в котором хранятся состояния каждой из клеток.
            При инициации заполняется символами моря '○'.
        ships : list
            Список кораблей доски.
        locked_dots : list
            Список заблокированных точек: во время генерации случайной доски
            служит для хранения уже занятых кораблями и их ореолами точек, а
            во время игры служит для хранения точек, куда игрок уже стрелял.
        live_ships : int
            Количество живых кораблей на доске.
        """

        self.table = [['○'] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ships = list()
        self.locked_dots = list()
        self.live_ships = len(SHIPS_TYPES)

    @property
    def is_hidden(self) -> bool:
        """
        Геттер для параметра _is_hidden
        """

        return self._is_hidden

    @is_hidden.setter
    def is_hidden(self, value: bool) -> None:
        """
        Сеттер для параметра _is_hidden
        """

        if isinstance(value, bool):
            self._is_hidden = value
        else:
            raise ValueError('Параметр is_hidden должен быть True или False.')

    def add_ship(self, ship: Ship) -> None:
        """
        Ставит корабль на доску (если не получается, выбрасывает исключение).
        """

        # Проверяем возможность установки всех точек корабля
        for dot in ship.dots:
            if Board.out(dot) or dot in self.locked_dots:
                raise BoardWrongShipException()
        # Устанавливаем на доску корабль
        for dot in ship.dots:
            self.table[dot.x][dot.y] = '■'
            self.locked_dots.append(dot)
        # Добавляем корабль в список кораблей доски
        self.ships.append(ship)
        # Отмечаем ореол корабля
        self.mark_oreol(ship)

    def mark_oreol(self, ship: Ship, is_game: bool = False) -> None:
        """
        Формирует ореол корабля, т.е. помечает точки вокруг,
        где другого корабля по правилам быть не может.
        """

        # Смещения координат для нахождения всех соседей данной точки
        neighbours = [(-1, -1), (0, -1), (1, -1), (-1, 0),
                      (1, 0), (-1, 1), (0, 1), (1, 1)]
        # Для каждой точки корабля и для всех её соседей
        for dot in ship.dots:
            for dx, dy in neighbours:
                x, y = dot.x + dx, dot.y + dy
                current_dot = Dot(x, y)
                # Если сосед в пределах доски и не был помечен ранее
                if (not Board.out(current_dot)) and \
                   (current_dot not in self.locked_dots):
                    # Помечаем соседа
                    self.locked_dots.append(current_dot)
                    # Если идёт игра, отмечаем ореол на доске
                    if is_game:
                        self.table[x][y] = '•'

    def show(self) -> None:
        """
        Выводит доску в консоль в зависимости от параметра _is_hidden.
        """

        print(' X| 1 2 3 4 5 6')
        print('Y◢ ____________')
        for row in range(BOARD_SIZE):
            print(row + 1, end=' | ')
            for col in range(BOARD_SIZE):
                cell = self.table[col][row]
                if self.is_hidden:
                    # Прячем ещё живые корабли соперника
                    print('○', end=' ') if cell == '■' else print(cell, end=' ')
                else:
                    print(cell, end=' ')
            print('')
        print('\n')

    @staticmethod
    def out(dot: Dot) -> bool:
        """
        Возвращает True , если точка выходит за пределы доски,
        и False, если не выходит.
        """

        return not (0 <= dot.x < BOARD_SIZE and 0 <= dot.y < BOARD_SIZE)

    def shot(self, dot: Dot) -> bool:
        """
        Делает выстрел по доске.
        Если есть попытка выстрелить за пределы доски или
        в использованную точку, то выбрасывает исключения.
        Возвращает True, если право следующего хода остаётся за текущим игроком
        и False, если право следующего хода переходит сопернику.
        """

        # Если выстрел за пределы доски
        if Board.out(dot):
            raise BoardOutException
        # Если выстрел в уже стрелянную точку
        if dot in self.locked_dots:
            raise BoardUsedException
        # Добавляем точку в список уже стрелянных
        self.locked_dots.append(dot)
        # Для каждого корабля на доске
        for ship in self.ships:
            # Если есть попадание
            if ship.is_strike(dot):
                # Отнимаем жизнь у корабля
                ship.lives -= 1
                # Помечаем точку на доске
                self.table[dot.x][dot.y] = '×'
                # Если это потопление
                if ship.lives == 0:
                    # Уменьшаем количество живых кораблей
                    self.live_ships -= 1
                    # Отмечаем ореол вокруг потопленного корабля
                    self.mark_oreol(ship, is_game=True)
                    # Сообщаем о потоплении
                    print('\n\tКорабль потоплен!')
                    sleep(1)
                    # У текущего игрока сохраняется право следующего хода
                    return True
                # Попал, но не потопил
                else:
                    # Сообщаем о попадании
                    print('\n\tПопадание!')
                    sleep(1)
                    # У текущего игрока сохраняется право следующего хода
                    return True
        # Нет попадания
        # Помечаем точку на доске
        self.table[dot.x][dot.y] = '•'
        # Сообщаем о промахе
        print('\n\tМимо.')
        sleep(1)
        # Право следующего хода переходит сопернику
        return False

    def get_ready(self) -> None:
        """
        Обнуляет перед стартом игры список заблокированных точек,
        который использовался во время генерации доски.
        """

        self.locked_dots = list()

    def is_loser(self) -> bool:
        """
        Проверяет состояние проигрыша.
        """

        return self.live_ships == 0


class Player():
    """
    Родительский класс для представления игроков.

    Атрибуты
    --------
    own_board : Board
        Собственная доска.
    opponent_board: Board
        Доска соперника.

    Методы
    --------
    ask():
        Спрашивает игрока, в какую клетку он делает выстрел.
        Потомки должны реализовать этот метод.
    move():
        Делает ход в игре.
        Вызывает метод ask() и делает выстрел по доске соперника,
        если есть исключения, повторяет попытку сделать ход.
        Возвращает True, если право следующего хода остаётся за текущим игроком
        и False, если право следующего хода переходит сопернику.
    """

    def __init__(self, own_board: Board, opponent_board: Board) -> None:
        """
        Устанавливает все необходимые атрибуты для объекта Player.

        Атрибуты
        --------
        own_board : Board
            Собственная доска.
        opponent_board: Board
            Доска соперника.
        """

        self.own_board = own_board
        self.opponent_board = opponent_board

    def ask(self):
        """
        Спрашивает игрока, в какую клетку он делает выстрел.
        Потомки должны реализовать этот метод.
        """

        raise NotImplementedError(f'Определите ask в {self.__class__.__name__}.')

    def move(self) -> bool:
        """
        Делает ход в игре.
        Вызывает метод ask() и делает выстрел по доске соперника,
        если есть исключения, повторяет попытку сделать ход.
        Возвращает True, если право следующего хода остаётся за текущим игроком
        и False, если право следующего хода переходит сопернику.
        """

        while True:
            try:
                return self.opponent_board.shot(self.ask())
            except ValueError:
                print('\n\tВнимательнее, вводите две цифры через пробел.\n')
                sleep(1)
            except BoardException as e:
                print(e)
                sleep(1)


class AI(Player):
    """
    Класс для представления игрока-компьютера.

    Наследуемые атрибуты
    --------
    own_board : Board
        Собственная доска.
    opponent_board: Board
        Доска соперника.

    Наследуемые методы
    --------
    move():
        Делает ход в игре.
        Вызывает метод ask() и делает выстрел по доске соперника,
        если есть исключения, повторяет попытку сделать ход.
        Возвращает True, если право следующего хода остаётся за текущим игроком
        и False, если право следующего хода переходит сопернику.

    Методы
    --------
    ask():
        Спрашивает игрока, в какую клетку он делает выстрел.
        Для AI это будет выбор случайной точки.
    """

    def ask(self) -> Dot:
        """
        Спрашивает игрока, в какую клетку он делает выстрел.
        Для AI это будет выбор случайной точки.
        """

        x, y = randint(1, BOARD_SIZE), randint(1, BOARD_SIZE)
        print(f'x y = {x} {y}')
        sleep(1)
        return Dot(x - 1, y - 1)


class User(Player):
    """
    Класс для представления игрока-пользователя.

    Наследуемые атрибуты
    --------
    own_board : Board
        Собственная доска.
    opponent_board: Board
        Доска соперника.

    Наследуемые методы
    --------
    move():
        Делает ход в игре.
        Вызывает метод ask() и делает выстрел по доске соперника,
        если есть исключения, повторяет попытку сделать ход.
        Возвращает True, если право следующего хода остаётся за текущим игроком
        и False, если право следующего хода переходит сопернику.

    Методы
    --------
    ask():
        Спрашивает игрока, в какую клетку он делает выстрел.
    """

    def ask(self) -> Dot:
        """
        Спрашивает игрока, в какую клетку он делает выстрел.
        """

        x, y = input('x y = ').strip().split()
        if x and y:
            return Dot(int(x) - 1, int(y) - 1)
        else:
            raise ValueError


class Game():
    """
    Класс для представления игры.

    Атрибуты
    --------
    user : User
        Игрок-пользователь.
    user_board : Board
        Доска пользователя.
    ai : AI
        Игрок-компьютер, объект класса Ai .
    ai_board : Board
        Доска компьютера.

    Методы
    --------
    make_board():
        Возвращает готовую к игре доску с расставленными кораблями.
    @staticmethod
    random_board():
        Вспомогательная функция.
        Пытается сгенерировать случайную расстановку кораблей на пустой доске.
        В случае успеха возвращает объект Board, в ином случае None.
    @staticmethod
    greet():
        Приветствует в консоли пользователя и рассказывает о формате ввода.
    show_boards():
        Выводит на экран доски обоих игроков.
    loop():
        Игровой цикл.
        Поочерёдно для каждого игрока вызывается метод move() и
        выполняется проверка проигрыша доски соперника.
    start():
        Запуск игры. Сначала вызывается приветствие и запуск игры.
    """

    def __init__(self) -> None:
        """
        Устанавливает все необходимые атрибуты для объекта Game.

        Атрибуты
        --------
        user : User
            Игрок-пользователь.
        user_board : Board
            Доска пользователя.
        ai : AI
            Игрок-компьютер, объект класса Ai .
        ai_board : Board
            Доска компьютера.
        """

        self.user_board = self.make_board()
        self.ai_board = self.make_board()
        self.ai_board.is_hidden = True
        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    def make_board(self) -> Board:
        """
        Возвращает готовую к игре доску с расставленными кораблями.
        """

        board = None
        while board is None:
            board = Game.random_board()
        board.get_ready()
        return board

    @staticmethod
    def random_board() -> Board:
        """
        Вспомогательная функция.
        Пытается сгенерировать случайную расстановку кораблей на пустой доске.
        В случае успеха возвращает объект Board, в ином случае None.
        """

        # Создаём пустую доску
        board = Board()
        # Устанавливаем счётчик попыток
        attempts = 0
        # Для каждого типа корабля, от самого большого к самому маленькому
        for length in SHIPS_TYPES:
            # Начинаем попытки поставить корабль
            while True:
                # Если число попыток превышено, то сдаёмся и начинаем заново
                if attempts > 2000:
                    return None
                # Пытаемся поставить нос корабля в случайную точку и
                # расположить его в случайном направлении
                try:
                    board.add_ship(Ship(length,
                                        Dot(randint(0, BOARD_SIZE-1),
                                            randint(0, BOARD_SIZE-1)
                                            ),
                                        randint(0, 1)
                                        )
                                   )
                    break
                except BoardWrongShipException:
                    pass
                # Увеличиваем счётчик попыток
                attempts += 1
        # Возвращаем доску с расставленными кораблями
        return board

    @staticmethod
    def greet() -> None:
        """
        Приветствует в консоли пользователя и рассказывает о формате ввода.
        """


        text = """
        Привет Путник! Это игра «Морской бой».
        Бой идёт до полного уничтожения одной из сторон.
        Координаты выстрела вводятся цифрами через пробел:
        \t координата по горизонтали (X), пробел, координата по вертикали (Y)
        """
        marks = """
        Обозначения:
            ■ - палуба
            • - мимо / ореол корабля
            ○ - море
            × - попадание
        """

        print(text)
        print(marks)
        input('\n\tНажмите -= Enter =- для старта')

    def show_boards(self) -> None:
        """
        Выводит на экран доски обоих игроков.
        """

        print('\n\n\n' + '-' * 50)
        print('Доска пользователя:\n')
        self.user.own_board.show()
        print('Доска компьютера:\n')
        self.ai.own_board.show()

    def loop(self) -> None:
        """
        Игровой цикл.
        Поочерёдно для каждого игрока вызывается метод move() и
        выполняется проверка проигрыша доски соперника.
        """

        # Маркер текущего игрока
        player = 0
        # Игровой цикл
        while True:
            # Выводим на экран доски обоих игроков
            self.show_boards()
            # Делаем ход текущим игроком
            if player % 2 == 0:
                print('Ваш ход:')
                repeat = self.user.move()
            else:
                print('Ходит компьютер:')
                repeat = self.ai.move()
            # Переход / сохранение права следующего хода
            player += 0 if repeat else 1
            # Если игрок-компьютер проиграл
            if self.ai.own_board.is_loser():
                print('\n\n\n' + '-' * 50 + '\n\n\n')
                print('#' * 22 + '\n#    Вы выиграли!    #\n' + '#' * 22)
                self.show_boards()
                break
            # Если игрок-пользователь проиграл
            if self.user.own_board.is_loser():
                print('\n\n\n' + '-' * 50 + '\n\n\n')
                print('#' * 22 + '\n# Компьютер выиграл! #\n' + '#' * 22)
                self.show_boards()
                break

    def start(self) -> None:
        """
        Запуск игры. Сначала вызывается приветствие, затем игровой цикл.
        """

        Game.greet()
        self.loop()


if __name__ == '__main__':
    game = Game()
    game.start()
