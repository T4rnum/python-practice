import random
from typing import Literal

WORDS_BANK = {
    "Лёгкий": [
        "арбуз",
        "банан",
        "весна",
        "город",
        "дверь",
        "енот",
        "жираф",
        "замок",
        "игра",
        "книга",
        "лимон",
        "метро",
        "ножницы",
        "океан",
        "поезд",
        "рыба",
        "слон",
        "тигр",
        "утка",
        "флаг",
    ],
    "Средний": [
        "алгоритм",
        "библиотека",
        "вертолет",
        "галактика",
        "дерево",
        "интернет",
        "карандаш",
        "лабиринт",
        "монитор",
        "ноутбук",
        "облако",
        "пингвин",
        "программа",
        "ракета",
        "самолет",
        "телевизор",
        "уравнение",
        "фонарик",
        "хищник",
        "шахматы",
    ],
    "Сложный": [
        "абстракция",
        "асинхронность",
        "архитектура",
        "декомпозиция",
        "инкапсуляция",
        "криптография",
        "модификатор",
        "наследование",
        "оптимизация",
        "полиморфизм",
        "рекурсия",
        "сериализация",
        "синхронизация",
        "субстанция",
        "фреймворк",
        "цикличность",
        "человечность",
        "экспрессия",
        "экскаватор",
        "юриспруденция",
    ],
}


def get_word(difficulty: Literal["Лёгкий", "Средний", "Сложный"]) -> str:
    secret_word = random.choice(WORDS_BANK[difficulty])
    return secret_word.upper()


def start_dialog(
    actions: list, title="Выберите действие:", final_msg="Введите цифру:"
) -> int:
    print(title)
    for i, act in enumerate(actions, 1):
        print(f"[{i}] {act}")

    while True:
        user_input = input(final_msg + " ").strip()

        if user_input.isdigit():
            choice = int(user_input)
            if 1 <= choice <= len(actions):
                return choice - 1

        print(f"Ошибка! Введите число от 1 до {len(actions)}.")


def choose_max_attempts() -> int:
    while True:
        user_input = input(
            "Введите количество попыток (если останется 0 попыток - вас ПОВЕСЯТ!): "
        ).strip()
        try:
            max_attempts = int(user_input)
            if max_attempts > 0:
                return max_attempts
            else:
                print(
                    "Вас повесили на месте, это самый быстрый проигрыш! Попробуем ещё раз..."
                )
        except ValueError:
            print("Ошибка! Введите корректное целое число больше 0!")


def display_hangman(attempts_left: int, max_attempts: int):
    health = attempts_left / max_attempts if max_attempts > 0 else 0

    if health > 0.5:
        head_top = " (•_•) "  # Бодрый челик
    elif health > 0:
        head_top = " (o_o) "  # Начинает паниковать
    else:
        head_top = " (X_X) "  # ПОТРАЧЕНО

    head = head_top if health <= 0.9 else ""
    torso = "|" if health <= 0.8 else ""
    left_a = "/" if health <= 0.6 else " "
    right_a = "\\" if health <= 0.5 else " "
    ass = "|" if health <= 0.4 else ""
    left_l = "/" if health <= 0.2 else " "
    right_l = "\\" if health <= 0.00 else " "

    arms_line = f"{left_a}{torso}{right_a}"
    legs_line = f"{left_l} {right_l}"

    print(f"""
        --------
        |      |
        |   {head}
        |     {arms_line}
        |      {ass}
        |     {legs_line}
        |
        -
    """)


def display_word(word: str, guessed_letters: list[str]):
    chars = []
    for char in word:
        if char in guessed_letters:
            chars.append(char)
        else:
            chars.append("_")
    print(" ".join(chars))


def input_letter() -> str:
    while True:
        user_input = input("Введите букву: ").strip().upper()

        if len(user_input) == 1 and user_input.isalpha():
            return user_input
        else:
            print("Необходимо ввести букву!")


def game_loop(word: str, max_attempts: int) -> bool:
    tries = 0
    attempts_left = max_attempts
    guessed_letters: list[str] = []
    used_letters: list[str] = []
    while True:
        display_hangman(attempts_left, max_attempts)
        display_word(word, guessed_letters)
        print(f"Осталось попыток: {attempts_left}")
        print(f"Использованы буквы: {' '.join(used_letters)}")
        letter = input_letter()

        if letter in used_letters:
            print("Вы уже вводили эту букву!")
            continue
        used_letters.append(letter)

        if letter in word:
            guessed_letters.append(letter)
            if set(word).issubset(guessed_letters):
                print(rf"""
               . : .
             '   .   '
         .  * \ /   * .
          .  * --x-- * .
         .  * / \   * .
             .   .   .
               ' : '
  \       /             \       /
   \     /               \     /
    \___/                 \___/
    (o_o)  ПОБЕДА-А-А-А!  (•_•)
    <) )>                 <) )>
    /   \                 /   \
=====================================
 Поздравляем! Вы угадали слово: {word}
=====================================
""")
                return True
        else:
            tries += 1
            attempts_left = max_attempts - tries
            if attempts_left <= 0:
                display_hangman(attempts_left, max_attempts)
                print("П О Т Р А Ч Е Н О !")
                print(f"Вы не угадали слово: {word}")
                return False


def start_play():
    total_wins = 0
    total_loses = 0
    while True:
        print("Добро пожаловать на виселицу!")

        difficults = ["Лёгкий", "Средний", "Сложный"]
        difficult_index = start_dialog(difficults, title="Выберите сложность:")
        word = get_word(difficults[difficult_index])
        max_attempts = choose_max_attempts()

        is_won = game_loop(word, max_attempts)

        if is_won:
            total_wins += 1
        else:
            total_loses += 1

        is_exit = start_dialog(["Да", "Нет"], "Хотите продолжить?") == 1

        if is_exit:
            print("До встречи на виселице!")
            print(f"Всего побед: {total_wins}")
            print(f"Всего поражений: {total_loses}")
            break


start_play()
