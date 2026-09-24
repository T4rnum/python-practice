from datetime import datetime
import msvcrt
import ctypes

''' Что можно доделать
1. Отключить курсор там где не надо ничего вводить
2. Сделать полный вид календаря (3x4 таблица месяцев)
3. Сделать отображение доп информации (Високосный ли год, год какого животного)
4. Переделать выбор опции в календаре, чтобы листались месяцы на левую и правую стрелки, а на верх/низ можно было выбирать опцию, как в основном меню
'''
# Включаем поддержку ANSI-кодов в стандартной консоли Windows
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

menu_operations = {
    0 : '[1] Вывести календарь на определённый год',
    1 : '[2] Вывести текущий месяц и год',
    2 : '[ESC] Выход'
}

current_menu_operation = 0
current_month = 0

def draw_menu(current_menu_operation = 0, menu_operations = menu_operations):
    print("\033[H\033[J", end="")
    print('Выберите действие')
    for operation in menu_operations:
        if operation == current_menu_operation:
            print('>', menu_operations[operation], '<')
        else:
            print(menu_operations[operation])

def run_operation(selected_operation):
    calendar_options = {
        0 : '[↑][↓] Предыдущий/следующий месяц',
        1 : '[1] Выбрать год',
        2 : '[2] Развернуть/свернуть календарь',
        3 : '[ESC] В главное меню'
    }
    current_calendar_option = 0
    print("\033[H\033[J", end="")
    current_month = 0
    year = datetime.now().year
    if selected_operation == 0:
        while True:
                try:
                    year = int(input('Введите год: '))

                    if year < 1:
                        print("Такого года не существует, попробуйте ввести ещё раз")
                        continue

                    break
                except ValueError:
                    print("Такого года не существует, попробуйте ввести ещё раз")
    else:
        current_month = datetime.now().month - 1
    while True:
        print_month(current_month, year)
        for option in calendar_options:
            print(calendar_options[option])

        key = msvcrt.getch()

        if key == b'1': # 1
            print('Выбран первый вариант')
            break
        elif key == b'2': # 2
            print('Выбран второй вариант')
            break
        elif key == b'H': # Стрелка вверх
            new_month = current_month - 1
            if new_month >= 0:
                current_month = new_month
            elif year > 1:
                current_month = 11
                year -= 1
            continue
        elif key == b'P': # Стрелка вниз
            new_month = current_month + 1
            if new_month <= 11:
                current_month = new_month
            else:
                current_month = 0
                year += 1
            continue
        elif key == b'\x1b': # ESC
            break
        print(key)


def print_month(current_month, year):
    months = [
        ('Январь', 31),
        ('Февраль', 29 if is_leap_year(year) else 28),
        ('Март', 31),
        ('Апрель', 30),
        ('Май', 31),
        ('Июнь', 30),
        ('Июль', 31),
        ('Август', 31),
        ('Сентябрь', 30),
        ('Октябрь', 31),
        ('Ноябрь', 30),
        ('Декабрь', 31)
    ]
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    p_year = year - 1
    total_days = 365 * p_year + p_year // 4 - p_year // 100 + p_year // 400
    days_of_weeks = [[] for _ in range(7)]

    for month in range(current_month):
        total_days += months[month][1]

    for empty_day in range(total_days % 7):
        days_of_weeks[empty_day].append(' ')

    for day in range(months[current_month][1]):
        days_of_weeks[(total_days + day) % 7].append(day + 1)

    calendar_header = "  ".join(days)
    year_header = f'{months[current_month][0]} {year}'
    header_separation_length = (len(calendar_header) - len(f' {year_header} ')) // 2
    if header_separation_length < 0:
        header_separation_length = 0

    separation = '=' * header_separation_length

    print("\033[H\033[J", end="")
    print(separation, year_header, separation + '=' if len(year_header) % 2 != 0 else separation)
    print(calendar_header)
    max_len = max(len(days) for days in days_of_weeks)
    for i in range(max_len):
        row = []
        for days in days_of_weeks:
            row.append(f"{days[i]:<2}" if i < len(days) else "  ")
        print("  ".join(row))
    print('=' * len(calendar_header))

while True:
    draw_menu(current_menu_operation)
    key = msvcrt.getch()

    if key == b'1': # 1
        run_operation(0)
        continue
    elif key == b'2': # 2
        run_operation(1)
        continue
    elif key == b'\r': # Enter
        if current_menu_operation == 0 or current_menu_operation == 1:
            run_operation(current_menu_operation)
        else:
            break
        continue
    elif key == b'H': # Стрелка вверх
        current_menu_operation = (current_menu_operation - 1) % len(menu_operations)
        continue
    elif key == b'P': # Стрелка вниз
        current_menu_operation = (current_menu_operation + 1) % len(menu_operations)
        continue
    elif key == b'\x1b': # ESC
        break
