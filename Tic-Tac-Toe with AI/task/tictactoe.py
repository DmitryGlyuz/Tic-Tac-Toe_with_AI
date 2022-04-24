import re


class Table(list):
    def __init__(self, cells_string: str = "_________"):
        super().__init__()
        # Splitting a string with symbols into rows in the table
        for i in range(0, 8, 3):
            current_row = cells_string.replace('_', ' ')[i:i+3]
            # Append row to the table as a list with chars
            self.append(list(current_row))
        self.current_player_sign = 'X' if cells_string.count('X') <= cells_string.count('O') else "O"

    def vertical_lines(self) -> list:
        return list(map(list, zip(*self)))

    def diagonals(self) -> list:
        return [[self[i][i] for i in range(3)],
                [self[i][2 - i] for i in range(3)]]

    def all_lines(self) -> list:
        return self + self.vertical_lines() + self.diagonals()

    def has_empty_cells(self) -> bool:
        return any(map(lambda line: ' ' in line, self.all_lines()))

    @staticmethod
    def three_in_line(line: list[str]) -> str:
        return line[0] if line.count(line[0]) == 3 and line[0] != ' ' else ''

    @staticmethod
    def convert_coordinates(other_method):
        def wrapper(self, _coordinates):
            return other_method(self, *map(lambda it: int(it) - 1, _coordinates.split(' ')))
        return wrapper

    @convert_coordinates
    def set_sign(self, _x: int, _y: int):
        self[_x][_y] = self.current_player_sign

    @convert_coordinates
    def is_cell_occupied(self, _x: int, _y: int) -> bool:
        return self[_x][_y] != ' '

    def __str__(self) -> str:
        horizontal_line = "-" * 9
        output = horizontal_line + '\n'
        for row in self:
            output += f"| {' '.join(row)} |\n"
        return output + horizontal_line


class Player:
    def __init__(self, _table):
        self.table = _table

    def make_move(self, coordinates):
        if re.fullmatch(r"[1-3] [1-3]", coordinates):
            if self.table.is_cell_occupied(coordinates):
                raise ValueError("This cell is occupied! Choose another one!")
            else:
                self.table.set_sign(coordinates)
                return True
        elif re.match(r'\d+ \d+', coordinates):
            raise ValueError("Coordinates should be from 1 to 3!")
        else:
            raise ValueError("You should enter numbers!")


class Game:
    def __init__(self, _table: Table):
        self.table = _table

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
        elif self.table.has_empty_cells():
            return "Game not finished"
        elif not self.table.has_empty_cells():
            return "Draw"


table = Table(input("Enter the cells: "))
player = Player(table)
game = Game(table)

print(table)

successful_move = False
while not successful_move:
    try:
        successful_move = player.make_move(input("Enter the coordinates:"))
    except ValueError as error_message:
        print(error_message)

print(game.state())
print(table)
