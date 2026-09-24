from random import choice, randint

N = 10
game_board = [[0] * N for _ in range(N)]
size_ships = (4, 3, 3, 2, 2, 2, 1, 1, 1, 1)


# здесь продолжайте программу
Coords = list[tuple[int, int]]


def random_deploy_ships(
    game_board: list[list[int]], size_ships: tuple[int], board_size: int
) -> None:
    for ship_size in size_ships:
        ship_coords = get_ship_coords(ship_size, board_size, game_board)
        for i, j in ship_coords:
            game_board[i][j] = 1


def get_ship_coords(
    ship_size: int, board_size: int, game_board: list[list[int]]
) -> Coords:
    while True:
        if choice((True, False)):  # Горизонтальный или вертикальный корабль
            row = randint(0, board_size - 1)
            col = randint(0, board_size - 1 - ship_size)
            ship_coords = [(row, c) for c in range(col, col + ship_size)]
        else:
            row = randint(0, board_size - 1 - ship_size)
            col = randint(0, board_size - 1)
            ship_coords = [(r, col) for r in range(row, row + ship_size)]

        if check_neighbours_coords(ship_coords, board_size, game_board):
            return ship_coords


def check_neighbours_coords(
    ship_coords: Coords, board_size: int, game_board: list[list[int]]
) -> bool:
    for row, col in ship_coords:
        total = sum(
            game_board[i][j]
            for i in range(row - 1, row + 2)
            for j in range(col - 1, col + 2)
            if 0 <= i < board_size and 0 <= j < board_size
        )
        if total != 0:
            return False
    return True


random_deploy_ships(game_board, size_ships, N)

for row in game_board:
    print(*row)
