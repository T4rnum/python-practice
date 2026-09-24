import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import uniform
from typing import Literal

# ========== Абстрактные классы предметов ==========


class ItemUsageError(Exception):
    def __init__(
        self,
        message: str = (
            "Невозможно использовать предмет, количество которого меньше или равно 0"
        ),
    ):
        self.message = message
        super().__init__(self.message)


Rarity = Literal["common", "rare", "epic", "legendary"]


@dataclass
class Item(ABC):
    """Абстрактный класс для создания предметов"""

    name: str
    description: str
    rarity: Rarity
    count: int

    @abstractmethod
    def get_type(self) -> str:
        """Возвращает тип предмета, например: 'Оружие'"""


@dataclass
class WeaponItem(Item):
    """Абстрактный класс для создания предметов оружия"""

    @abstractmethod
    def attack(self) -> int:
        """Метод атаки оружия, возвращает нанесённый урон"""

    def get_type(self) -> str:
        return "Оружейный предмет"


@dataclass
class DefendItem(Item):
    """Абстрактный класс для создания защитных предметов"""

    @abstractmethod
    def defend(self) -> int:
        """Метод защиты предмета, возвращает наложенную от него защиту"""

    def get_type(self) -> str:
        return "Защитный предмет"


@dataclass
class ConsumeItem(Item):
    """Абстрактный класс для создания предметов-расходников"""

    @abstractmethod
    def consume(self) -> None:
        """Метод использования предмета
        (Не забудь удалить предмет после использования)"""

    def get_type(self) -> str:
        return "Расходуемый предмет"


@dataclass
class QuestItem(Item):
    """Абстрактный класс для создания квестовых предметов"""

    @abstractmethod
    def use(self) -> None:
        """Метод использования предмета,
        вызывается по выполнению квеста, связанного с этим предметом"""

    def get_type(self) -> str:
        return "Квестовый предмет"


# ========== Классы предметов ==========


@dataclass
class Sword(WeaponItem):
    """Класс для создания экземпляра меча"""

    damage: int
    crit_chance: float
    crit_multiplier: float

    def attack(self) -> int:
        if self.count <= 0:
            raise ItemUsageError()
        if round(self.crit_chance, 2) >= round(uniform(0, 100), 2):
            return int(self.damage * self.crit_multiplier)
        return self.damage


@dataclass
class HealthPotion(ConsumeItem):
    """Класс для создания экземпляра лечебного зелья"""

    restore_points: int

    def consume(self) -> None:
        if self.count > 0:
            print(
                f"Зелье '{self.name}' использовано! "
                f"Было восстановлено {self.restore_points} hp!"
            )
            self.count -= 1
        else:
            raise ItemUsageError()


# ========== Сервисные классы для EquipmentManager ==========


OwnerItems = dict[str, list[Item] | str]


class EMExporter(ABC):
    """Абстрактный класс для создания экспортёров экземпляра EquipmentManager"""

    @abstractmethod
    def export(self, owner_name: str, items: list[Item], filepath: str) -> None:
        """Метод экспорта экземпляра EquipmentManager"""


class EMJSONExporter(EMExporter):
    """Экспорт экземпляра EquipmentManager в формате .json"""

    def export(self, owner_name: str, items: list[Item], filepath: str) -> None:
        payload: OwnerItems = {"owner": owner_name, "items": items}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                payload, f, ensure_ascii=False, indent=2, default=self.serialize_item
            )

    @staticmethod
    def serialize_item(item: Item) -> dict[str, str]:
        return {
            "name": item.name,
            "type": item.get_type(),
            "rarity": item.rarity,
            "description": item.description,
            "count": str(item.count),
        }


class EMTextExporter(EMExporter):
    """Экспорт экземпляра EquipmentManager в формате .txt"""

    def export(self, owner_name: str, items: list[Item], filepath: str) -> None:
        lines = [f"Owner: {owner_name}"]
        for item in items:
            lines.append(
                f"""- {item.name} ({item.get_type()}):
    Редкость: {item.rarity},
    Описание: {item.description},
    Кол-во: {item.count}"""
            )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


# ========== EquipmentManager ==========


class EquipmentManager:
    """Управляет добавлением предметов в экипировку"""

    def __init__(self, owner_name: str) -> None:
        self.owner_name = owner_name
        self._items: list[Item] = []

    def add_item(self, item: Item) -> None:
        """Добавляет предмет в экипировку"""

        self._items.append(item)

    def export_inventory(self, filepath: str, exporter: EMExporter):
        """Экспортирует экземпляр в выбранный формат документа,
        используя для этого переданный экспортёр"""

        exporter.export(self.owner_name, self._items, filepath)


# ========== main.py ==========


# Создаём предметы
iron_sword = Sword("Железный меч", "Старый, да удалый", "common", 1, 12, 10, 1.5)
small_health_potion = HealthPotion(
    "Здоровье 1", "Восстанавливает немного здоровья", "common", 10, 25
)

# Тест использования предметов
print(f"Было нанесено {iron_sword.attack()} урона!")
small_health_potion.consume()

# Создаем менеджер инвентаря
manager = EquipmentManager(owner_name="Vlad")
manager.add_item(iron_sword)
manager.add_item(small_health_potion)

# Экспортируем через нужный экспортер (DIP в действии)
json_exporter = EMJSONExporter()
manager.export_inventory(filepath="inventory.json", exporter=json_exporter)

txt_exporter = EMTextExporter()
manager.export_inventory(filepath="inventory.txt", exporter=txt_exporter)
