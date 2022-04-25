import random
import re
from itertools import chain, product


class Table(list[list]):
    def __init__(self):
        super().__init__()
        for i in range(3):
            self.append([' '] * 3)

    def vertical_lines(self) -> list:
        return list(map(list, zip(*self)))

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

    def set_sign(self, sign: str, x: int, y: int):
        self[x][y] = sign

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
        if re.fullmatch(r"[1-3] [1-3]", user_input):
            coordinates = tuple(map(lambda it: int(it) - 1, user_input.split(' ')))
            if self.table.is_cell_occupied(*coordinates):
                raise ValueError("This cell is occupied! Choose another one!")
            else:
                self.table.set_sign(self.sign, *coordinates)
                self.moves_counter += 1
        elif re.match(r'\d+ \d+', user_input):
            raise ValueError("Coordinates should be from 1 to 3!")
        else:
            raise ValueError("You should enter numbers!")

    def random_move(self):
        self.table.set_sign(self.sign, *random.choice(self.table.free_cells()))


class Game:
    def __init__(self, _table: Table, first_player: Player, second_player: Player):
        self.table = _table
        self.first_player = first_player
        self.second_player = second_player
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


table = Table()
user = Player("user", 'X', table)
computer = Player("easy", 'O', table)
game = Game(table, user, computer)


def user_turn():
    moves = user.moves_counter
    while moves == user.moves_counter:
        try:
            user.manual_move(input("Enter the coordinates: "))
        except ValueError as error_message:
            print(error_message)


def make_move_by(player: Player):
    if player.type == "user":
        user_turn()
    else:
        print(f'Making move level "{player.type}"')
        player.random_move()


print(table)
while not game.is_over():
    make_move_by(game.current_player())
    print(table)
print(game.state())
