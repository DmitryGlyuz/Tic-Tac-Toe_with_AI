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
        result = [list() for _ in range(3)]
        for row in self:
            for i in range(3):
                result[i].append(row[i])
        return result

    def diagonals(self) -> list:
        result = [list() for _ in range(2)]
        for i in range(3):
            result[0].append(self[i][i])
            result[1].append(self[2 - i][i])
        return result

    def all_lines(self) -> list:
        return self + self.vertical_lines() + self.diagonals()

    def has_empty_cells(self) -> bool:
        return any(map(lambda line: ' ' in line, self.all_lines()))

    @staticmethod
    def three_in_line(line: list[str]) -> str:
        return line[0] if line.count(line[0]) == 3 and line[0] != ' ' else ''

    def winner(self) -> str:
        for line in self.all_lines():
            winner = self.three_in_line(line)
            if winner:
                return winner
        else:
            return ''

    @staticmethod
    def convert_coordinates(other_method):
        def wrapper(self, _coordinates):
            return other_method(self, *map(lambda it: int(it) - 1, _coordinates.split(' ')))
        return wrapper

    @convert_coordinates
    def make_move(self, _x: int, _y: int):
        self[_x][_y] = self.current_player_sign

    @convert_coordinates
    def is_cell_occupied(self, _x: int, _y: int) -> bool:
        return self[_x][_y] != ' '

    def __str__(self) -> str:
        horizontal_line = "---------"
        output = horizontal_line + '\n'
        for row in self:
            output += "| "
            for sign in row:
                output += sign + ' '
            output += "|\n"
        return output + horizontal_line


table = Table(input("Enter the cells: "))


print(table)
while True:
    coordinates = input("Enter the coordinates:")
    if re.fullmatch(r"[1-3] [1-3]", coordinates):
        if table.is_cell_occupied(coordinates):
            print("This cell is occupied! Choose another one!")
        else:
            table.make_move(coordinates)
            break
    elif re.match(r'\d+ \d+', coordinates):
        print("Coordinates should be from 1 to 3!")
    else:
        print("You should enter numbers!")
print(table)
if table.has_empty_cells() and not table.winner():
    print("Game not finished")
elif not table.has_empty_cells() and not table.winner():
    print("Draw ")
elif table.winner():
    print(f"{table.winner()} wins")
