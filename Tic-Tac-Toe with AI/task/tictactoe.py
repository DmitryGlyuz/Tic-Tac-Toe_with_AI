from collections import Counter
import random
import re
from itertools import chain, product


class Cell:
    def __init__(self, value: str = ' '):
        self.value: str = value
        self.coordinates = 0, 0

    def __eq__(self, it):
        return it == self.value

    def __add__(self, it: str) -> str:
        return self.value + it

    def __str__(self):
        return self.value

    def __hash__(self):
        return self.value.__hash__()

    def set_mark(self, mark: str):
        self.value = mark

    def remove_mark(self):
        self.value = ' '

    def is_occupied(self):
        return self.value != ' '


class Table(list):
    def __init__(self):
        super().__init__()
        for i in range(3):
            self.append(tuple(Cell() for _ in range(3)))
            for j in range(3):
                self[i][j].coordinates = i, j

    def vertical_lines(self) -> tuple:
        return tuple(map(tuple, zip(*self)))

    def diagonals(self) -> tuple:
        return (tuple(self[i][i] for i in range(3)),
                tuple(self[i][2 - i] for i in range(3)))

    def all_marks(self) -> tuple:
        return tuple(chain(*self))

    def all_lines(self) -> tuple:
        return tuple(chain(self, self.vertical_lines(), self.diagonals()))

    def contains_empty_cells(self) -> bool:
        return ' ' in self.all_marks()

    def free_cells(self) -> list[tuple]:
        return [(i, j) for i, j in product(range(3), repeat=2) if not self[i][j].is_occupied()]

    @staticmethod
    def three_marks_on_line(line: list) -> str:
        return line[0].value if line.count(line[0].value) == 3 and line[0] != ' ' else ''

    @staticmethod
    def two_identical_marks_on_line(line: list[str]) -> str:
        counter = Counter(line)
        if counter[' '] == 1 and 2 in counter.values():
            return counter.most_common(1)[0][0]
        return ''

    def winner(self) -> str:
        for line in self.all_lines():
            winner = self.three_marks_on_line(line)
            if winner:
                return winner
        else:
            return ''

    def __str__(self) -> str:
        horizontal_line = "-" * 9
        output = horizontal_line + '\n'
        for row in self:
            output += "| "
            for cell in row:
                output += cell + ' '
            output += "|\n"
        return output + horizontal_line


class Player:
    def __init__(self, _type, _mark: str, _table: Table):
        self.type = _type
        self.table = _table
        self.mark = _mark
        self.moves_counter = 0

    def manual_move(self, user_input: str):
        if re.fullmatch(r"[1-3]\s+[1-3]", user_input):
            x, y = tuple(map(lambda it: int(it) - 1, re.split(r'\s+', user_input)))
            if self.table[x][y].is_occupied():
                raise ValueError("This cell is occupied! Choose another one!")
            else:
                self.table[x][y].set_mark(self.mark)
                self.moves_counter += 1
        elif re.match(r'\d+\s+\d+', user_input):
            raise ValueError("Coordinates should be from 1 to 3!")
        else:
            raise ValueError("You should enter numbers!")

    def random_move(self):
        (x, y) = random.choice(self.table.free_cells())
        self.table[x][y].set_mark(self.mark)

    def medium_move(self):
        for line in self.table.all_lines():
            if self.table.two_identical_marks_on_line(line):
                x, y = line[line.index(' ')].coordinates
                self.table[x][y].set_mark(self.mark)
                break
        else:
            self.random_move()

    def hard_move(self):
        def another_mark(current_mark: str) -> str:
            return 'X' if current_mark == 'O' else 'O'

        def minimax(table: Table, current_mark: str):
            winner = table.winner()
            if winner:
                return 1 if winner == self.mark else -1
            elif not table.contains_empty_cells():
                return 0
            else:
                scores = []
                for _x, _y in table.free_cells():
                    self.table[_x][_y].set_mark(current_mark)
                    scores.append(minimax(table, another_mark(current_mark)))
                    table[_x][_y].remove_mark()
                return max(scores) if current_mark == self.mark else min(scores)

        moves = dict.fromkeys(self.table.free_cells())
        for x, y in moves:
            self.table[x][y].set_mark(self.mark)
            moves[(x, y)] = minimax(self.table, another_mark(self.mark))
            self.table[x][y].remove_mark()
        x, y = max(moves, key=moves.get)
        self.table[x][y].set_mark(self.mark)


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

    def state(self) -> str:
        winner = self.table.winner()
        if winner:
            return f"{winner} wins"
        elif not self.table.contains_empty_cells():
            return "Draw"

    def is_over(self) -> bool:
        return self.table.winner() or not self.table.contains_empty_cells()


def user_move(player: Player):
    moves = player.moves_counter
    while moves == player.moves_counter:
        try:
            player.manual_move(input("Enter the coordinates: "))
        except ValueError as error_message:
            print(error_message)


def make_move_by(player: Player):
    if player.type == "user":
        user_move(player)
    else:
        print(f'Making move level "{player.type}"')
        match player.type:
            case 'easy':
                player.random_move()
            case 'medium':
                player.medium_move()
            case 'hard':
                player.hard_move()


def play_game(first_player_type, second_player_type):
    game = Game(Table(), first_player_type, second_player_type)
    print(game.table)
    while not game.is_over():
        make_move_by(game.current_player())
        print(game.table)
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
