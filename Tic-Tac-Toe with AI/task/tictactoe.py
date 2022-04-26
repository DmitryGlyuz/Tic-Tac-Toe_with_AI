from collections import Counter
import random
import re
from itertools import chain, product
from copy import deepcopy


class Cell(str):
    def __init__(self, value):
        self.value = value
        self.coordinates = 0, 0


class Table(list):
    def __init__(self):
        super().__init__()
        for i in range(3):
            self.append([])
            for j in range(3):
                self[i].append(Cell(' '))
                self[i][j].coordinates = i, j

    def vertical_lines(self) -> list:
        return list(zip(*self))

    def diagonals(self) -> list:
        return [[self[i][i] for i in range(3)],
                [self[i][2 - i] for i in range(3)]]

    def all_signs(self) -> tuple:
        return tuple(chain(*self))

    def all_lines(self) -> tuple:
        return tuple(chain(self, self.vertical_lines(), self.diagonals()))

    def contains_empty_cells(self) -> bool:
        return ' ' in self.all_signs()

    def free_cells(self) -> list[tuple]:
        return [(i, j) for i, j in product(range(3), repeat=2) if self[i][j] == ' ']

    @staticmethod
    def three_in_line(line: list[str]) -> str:
        return line[0] if line.count(line[0]) == 3 and line[0] != ' ' else ''

    @staticmethod
    def two_in_line(line: list[str]) -> str:
        counter = Counter(line)
        if counter[' '] == 1 and 2 in counter.values():
            return counter.most_common(1)[0][0]
        return ''

    def set_sign(self, sign: str, x: int, y: int):
        self[x][y] = sign

    def delete_sign(self, x: int, y: int):
        self[x][y] = ' '

    def is_cell_occupied(self, _x: int, _y: int) -> bool:
        return self[_x][_y] != ' '

    def __str__(self) -> str:
        horizontal_line = "-" * 9
        output = horizontal_line + '\n'
        for row in self:
            output += f"| {' '.join(row)} |\n"
        return output + horizontal_line


class Player:
    def __init__(self, _type, _sign: str, _table: Table):
        self.type = _type
        self.table = _table
        self.sign = _sign
        self.moves_counter = 0

    def manual_move(self, user_input: str):
        if re.fullmatch(r"[1-3]\s+[1-3]", user_input):
            coordinates = tuple(map(lambda it: int(it) - 1, re.split(r'\s+', user_input)))
            if self.table.is_cell_occupied(*coordinates):
                raise ValueError("This cell is occupied! Choose another one!")
            else:
                self.table.set_sign(self.sign, *coordinates)
                self.moves_counter += 1
        elif re.match(r'\d+\s+\d+', user_input):
            raise ValueError("Coordinates should be from 1 to 3!")
        else:
            raise ValueError("You should enter numbers!")

    def random_move(self):
        self.table.set_sign(self.sign, *random.choice(self.table.free_cells()))

    def smart_move(self):
        for line in self.table.all_lines():
            two_signs = self.table.two_in_line(line)
            if two_signs:
                x, y = line[line.index(' ')].coordinates
                self.table.set_sign(self.sign, x, y)
                break
        else:
            self.random_move()

    def ai_move(self):
        def winning(table: Table, player_sign: str):
            for line in table.all_lines():
                if table.two_in_line(line) == player_sign:
                    return True
            else:
                return False

        def minimax(table: Table, player_sign):
            enemy_sign = 'X' if player_sign == 'O' else 'O'
            if not table.contains_empty_cells():
                return 0
            elif winning(table, enemy_sign):
                return -10
            elif winning(table, player_sign):
                return 10
            else:
                result = 0
                new_table = deepcopy(table)
                for free_cell in new_table.free_cells():
                    new_table.set_sign(player_sign, *free_cell)
                    result += minimax(new_table, enemy_sign)
                return result

        moves = dict.fromkeys(self.table.free_cells())
        for cell in moves:
            self.table.set_sign(self.sign, *cell)
            moves[cell] = minimax(self.table, self.sign)
            self.table.delete_sign(*cell)
        best_move = max(moves, key=moves.get)
        self.table.set_sign(self.sign, *best_move)


class Game:
    def __init__(self, _table: Table, first_player_type: str, second_player_type: str):
        self.table = _table
        self.first_player = Player(first_player_type, 'X', self.table)
        self.second_player = Player(second_player_type, 'O', self.table)
        self.last_player = None
        self.first_players_move = True

    def current_player(self) -> Player:
        self.last_player = self.second_player if self.last_player == self.first_player else self.first_player
        return self.last_player

    def winner(self) -> str:
        for line in self.table.all_lines():
            winner = self.table.three_in_line(line)
            if winner:
                return winner
        else:
            return ''

    def state(self) -> str:
        winner = self.winner()
        if winner:
            return f"{winner} wins"
        elif not self.table.contains_empty_cells():
            return "Draw"

    def is_over(self) -> bool:
        return self.winner() or not self.table.contains_empty_cells()


def user_turn(player: Player):
    moves = player.moves_counter
    while moves == player.moves_counter:
        try:
            player.manual_move(input("Enter the coordinates: "))
        except ValueError as error_message:
            print(error_message)


def make_move_by(player: Player):
    if player.type == "user":
        user_turn(player)
    else:
        print(f'Making move level "{player.type}"')
        match player.type:
            case 'easy':
                player.random_move()
            case 'medium':
                player.smart_move()
            case 'hard':
                player.ai_move()


def play_game(first_player_type, second_player_type):
    table = Table()
    game = Game(table, first_player_type, second_player_type)

    print(table)
    while not game.is_over():
        make_move_by(game.current_player())
        print(table)
    print(game.state())


command = ''
while command != "exit":
    command = input("Input command: ")
    correct_start_conditions = (command.startswith('start '),
                                len(command.split(' ')) == 3,
                                all(map(lambda it: it in ("user", "easy", "medium", "hard"), command.split(' ')[1:])))
    if all(correct_start_conditions):
        play_game(*command.split(' ')[1:])
    elif command != 'exit' and not all(correct_start_conditions):
        print("Bad parameters!")
