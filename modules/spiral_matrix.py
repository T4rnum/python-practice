# ========== 1 Вариант ==========


rows, columns = (int(i) for i in input().split())

matrix = [[None for _ in range(columns)] for _ in range(rows)]

counter = 0
total_cells = rows * columns

top, bottom = 0, rows - 1
left, right = 0, columns - 1

while counter < total_cells:
    for i in range(left, right + 1):
        counter += 1
        matrix[top][i] = str(counter).ljust(3)
    top += 1
    if counter == total_cells:
        break

    for i in range(top, bottom + 1):
        counter += 1
        matrix[i][right] = str(counter).ljust(3)
    right -= 1
    if counter == total_cells:
        break

    for i in range(right, left - 1, -1):
        counter += 1
        matrix[bottom][i] = str(counter).ljust(3)
    bottom -= 1
    if counter == total_cells:
        break

    for i in range(bottom, top - 1, -1):
        counter += 1
        matrix[i][left] = str(counter).ljust(3)
    left += 1

for row in matrix:
    print(*row)


# ========== 2 Вариант ==========


N = int(input())

matrix = [[0] * N for _ in range(N)]

r, c = 0, 0  # Индексы строки и столбца
dr, dc = 0, 1  # dr: направление по строке, dc: направление по столбцу
top, bottom, left, right = 0, N - 1, 0, N - 1  # Границы

for num in range(1, N * N + 1):
    matrix[r][c] = num

    if dr == 0 and dc == 1 and c == right:
        dr, dc = 1, 0
        top += 1
    elif dr == 1 and dc == 0 and r == bottom:
        dr, dc = 0, -1
        right -= 1
    elif dr == 0 and dc == -1 and c == left:
        dr, dc = -1, 0
        bottom -= 1
    elif dr == -1 and dc == 0 and r == top:
        dr, dc = 0, 1
        left += 1

    r += dr
    c += dc

for row in matrix:
    print(*row)
