# Практика по Python

Сохранившиеся упражнения и небольшие проекты, написанные во время изучения Python. Это снимок учебной папки, а не полный дневник обучения: код в `learn.py` часто заменялся новым, поэтому предыдущие варианты здесь не восстановлены.

## Что лежит в репозитории

| Путь | Содержание |
| --- | --- |
| `learn.py` | Текущий черновик для коротких упражнений. |
| `modules/bank.py`, `modules/app.py` | Учебный пример классов аккаунта, платежей и логирования. Это демонстрация, а не настоящий банковский или безопасный сервис. |
| `modules/clean_inventory.py` | Модель предметов и экспорт инвентаря в JSON и текст. |
| `modules/spiral_matrix.py` | Упражнения со спиральным заполнением матрицы. |
| `progs/hangman.py` | Консольная игра «Виселица». |
| `progs/find_chain_words.py` | Поиск цепочки слов с изменением одной буквы за шаг. |
| `progs/sea_battle_deplot_ships.py` | Случайная расстановка кораблей для морского боя. |
| `progs/calendar_V1.py` | Консольный календарь для Windows (`msvcrt` и Windows API). |
| `progs/TurtleArt.py` | Рисование контуров изображения через Turtle и OpenCV. |
| `progs/4d_hyper_cube/` | Визуализация 4D-спирали с Pygame и PyOpenGL. |

## Как запускать

Примеры рассчитаны на Python 3.14 и запускаются из корня репозитория. Большинству хватает стандартной библиотеки:

```powershell
python progs/hangman.py
python progs/find_chain_words.py
python progs/sea_battle_deplot_ships.py
python modules/clean_inventory.py
python modules/app.py
```

`modules/clean_inventory.py` создаёт `inventory.json` и `inventory.txt`, а пример с логированием создаёт файл `modules/app-YYYY-MM-DD.log`. Эти результаты работы не включаются в репозиторий.

Для визуальных проектов установите дополнительные пакеты в своё виртуальное окружение:

```powershell
python -m pip install pygame-ce PyOpenGL opencv-python
python progs/4d_hyper_cube/main.py
```

`progs/TurtleArt.py` требует собственного изображения: укажите путь к нему в константе `INPUT_IMAGE` перед запуском. Исходное изображение в репозитории отсутствует. `progs/calendar_V1.py` запускается только в Windows.

Это учебные наброски разной степени готовности; общего приложения и единого набора тестов у папки нет.
