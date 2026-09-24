import turtle

import cv2

# ==========================================
# НАСТРОЙКИ
# ==========================================
INPUT_IMAGE = "progs/tat.jpg"  # Твоё фото
CANVAS_SIZE = 900  # Размер окна (чуть больше для красоты)

# Настройки детектора границ (Canny)
# Для чёрного фона лучше брать более чёткие границы
CANNY_LOW = 1
CANNY_HIGH = 80

# Скалирование (0.1 - 1.0). Чем больше, тем детальнее и дольше рисовка
SCALE_FACTOR = 1

# --- НАСТРОЙКИ СКОРОСТИ ---
# Обновлять экран каждые N сегментов.
# Поставь 1 для "медленно", 500 для "супер-турбо".
UPDATE_EVERY_N_SEGMENTS = 100
# ==========================================


def prepare_image(path):
    """Загружает, подготавливает цветную и контурную карты."""
    img = cv2.imread(path)
    if img is None:
        print(f"Ошибка: Не удалось найти файл {path}")
        exit()

    # Уменьшаем
    width = int(img.shape[1] * SCALE_FACTOR)
    height = int(img.shape[0] * SCALE_FACTOR)
    img_resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

    # Сохраняем цветную версию (OpenCV использует BGR, помним об этом)
    img_color = img_resized.copy()

    # Делаем карту границ
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)  # Исправленная опечатка!
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)  # Меньше размытия для чёткости
    edges = cv2.Canny(blurred, CANNY_LOW, CANNY_HIGH)

    return edges, img_color, width, height


def draw_art(edges, img_color, w, h):
    """Рисует цветными линиями на чёрном фоне в турбо-режиме."""

    # Находим контуры
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Настройка Экранa
    screen = turtle.Screen()
    screen.setup(CANVAS_SIZE, CANVAS_SIZE)
    screen.bgcolor("black")  # !!! ЧЁРНЫЙ ФОН !!!
    screen.colormode(255)  # !!! РЕЖИМ RGB ЦВЕТОВ (0-255) !!!
    screen.title("Turbo Color Engraving")
    screen.tracer(0, 0)  # Ручное управление обновлением

    t = turtle.Turtle()
    t.showturtle()
    t.shape("triangle")  # Треугольник выглядит динамичнее на скорости
    t.turtlesize(0.5, 0.5)
    t.speed(0)  # Максимальная внутренняя скорость
    t.width(1)

    scale = CANVAS_SIZE / max(w, h)

    print(f"Найдено контуров: {len(contours)}. Погнали!")

    segment_counter = 0

    for cnt in contours:
        if len(cnt) > 2:
            t.penup()

            # Первая точка контура
            x0, y0 = cnt[0][0]

            # --- БЕРЁМ ЦВЕТ С КАРТИНКИ ---
            # OpenCV хранит как [y, x], и в формате BGR (Blue, Green, Red)
            b, g, r = img_color[y0, x0]
            t.pencolor(r, g, b)  # Turtle нужен RGB
            # -----------------------------

            t.goto((x0 - w / 2) * scale, (h / 2 - y0) * scale)
            t.pendown()

            for point in cnt[1:]:
                x, y = point[0]

                # Обновляем цвет для каждого сегмента (для плавных переходов)
                b, g, r = img_color[y, x]
                t.pencolor(r, g, b)

                t.goto((x - w / 2) * scale, (h / 2 - y) * scale)

                # --- ТУРБО-ОБНОВЛЕНИЕ ---
                segment_counter += 1
                if segment_counter >= UPDATE_EVERY_N_SEGMENTS:
                    screen.update()  # Показываем огромный кусок сразу
                    segment_counter = 0

    # Финал
    screen.update()
    print("Готово!")
    screen.exitonclick()


if __name__ == "__main__":
    edge_map, color_map, width, height = prepare_image(INPUT_IMAGE)
    draw_art(edge_map, color_map, width, height)
