"""
Это модуль, в котором я накидал простые классы и систему логирования для них
Запускать программу необходимо через app.py, этот файл просто модуль с логикой
"""

import logging
from datetime import date
from logging.config import dictConfig
from typing import Any, Self


class ImportantFilter(logging.Filter):
    """
    Кастомный фильтр, который не пропускает записи ниже уровня WARNING
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.WARNING


class AccountOnlyFilter(logging.Filter):
    """
    Кастомный фильтр, который не пропускает записи если они попадают через логгер,
    название которого не начинается через __name__ + ".account", т.е. bank.account
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith(__name__ + ".account")


config: dict[str, Any] = {  # Словарь для инициализации логирования через конфиг
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s | %(levelname)-8s | %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "file": {
            "format": (
                "%(asctime)s | %(name)s | %(levelname)-8s "
                "| %(filename)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%H:%M:%S",
        },
    },
    "filters": {"important_filter": {"()": "bank.ImportantFilter"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "console",
            "filters": ["important_filter"],
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "filename": f"modules/app-{date.today()}.log",
            "encoding": "utf-8",
            "formatter": "file",
        },
    },
    "loggers": {
        "bank": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        "bank.account": {"level": "DEBUG", "propagate": True},
        "bank.payment": {"level": "DEBUG", "propagate": True},
    },
}

dictConfig(config)  # Инициализация логирования через словарь-конфиг

# Ниже закомментировано то же самое, что в словаре,
# только создание всех элементов идёт в самом коде

logger_bank = logging.getLogger(__name__)
# logger_bank.setLevel(logging.DEBUG)
logger_account = logging.getLogger(__name__ + ".account")
logger_payment = logging.getLogger(__name__ + ".payment")
# # logger_account.propagate = False
# # logger_payment.propagate = False

# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# console_handler.addFilter(ImportantFilter())

# file_handler = logging.FileHandler(f"app-{date.today()}.log", "w", encoding="utf-8")
# file_handler.setLevel(logging.DEBUG)
# # file_handler.addFilter(AccountOnlyFilter())

# console_formatter = logging.Formatter(
#     "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"
# )
# console_handler.setFormatter(console_formatter)

# file_formatter = logging.Formatter(
#     "%(asctime)s | %(name)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
#     datefmt="%H:%M:%S",
# )
# file_handler.setFormatter(file_formatter)

# logger_bank.addHandler(console_handler)
# logger_bank.addHandler(file_handler)


class DBSaveException(Exception):
    """
    Кастомное исключение для теста WARNING записи с Traceback
    """

    def __init__(self, message: str = "Ошибка при сохранении данных в БД") -> None:
        super().__init__(message)


class SystemException(Exception):
    """
    Кастомное исключение для теста CRITICAL записи с Traceback
    """

    def __init__(self, message: str = "Произошла системная ошибка") -> None:
        super().__init__(message)


class Account:
    """
    Для тестов логирования был создан простой аккаунт,
    который имеет имя и хеш пароля, а также может иметь систему платежей и защиты
    Ниже пара методов и свойств как раз для тестирования логов
    """

    __instances: list[Self] = []

    def __init__(self, name: str, psw: str) -> None:
        self.__name = name
        self.__psw = hash(psw)
        self.__instances.append(self)
        self._pay_sys = None
        self._guard_sys = None
        logger_account.info("Успешная регистрация в аккаунте")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__name}, {self.__psw})"

    @classmethod
    def log_in(cls, name: str, psw: str) -> Self | None:
        logger_account.debug("Проверка входных данных в аккаунт")
        for account in cls.__instances:
            if account.__name == name and account.__psw == hash(psw):
                logger_account.info("Успешная авторизация в аккаунте %s", account)
                return account
            elif account.__name == name:
                logger_account.warning(
                    "Совершена попытка входа в аккаунт %s, неверный пароль", account
                )
                if account.guard_sys:
                    account.guard_sys.get_warn()
                return None
        logger_account.info("Авторизация отменена, неверный логин или пароль")
        return None

    @property
    def pay_sys(self):
        return self._pay_sys

    @pay_sys.setter
    def pay_sys(self, sys: PaymentSystem):
        if sys.check_account(self):
            self._pay_sys = sys
        else:
            logger_account.warning("Попытка привязки чужой платёжной системы")
            if self.guard_sys:
                self.guard_sys.get_warn()

    @property
    def guard_sys(self):
        return self._guard_sys

    @guard_sys.setter
    def guard_sys(self, sys: GuardSystem):
        if sys.check_account(self):
            self._guard_sys = sys


class PaymentSystem:
    """
    Система платежей для аккаунта, здесь просто задаётся баланс в 1000 единиц,
    Можно снять деньги, если денег не хватает, то вызывается WARNING
    Также добавляется предупреждение через систему защиты
    """

    def __init__(self, account: Account) -> None:
        self.__account = account
        self.__account.pay_sys = self
        self.__money = 1000
        logger_payment.info("Успешная регистрация в платёжной системе")

    def pay(self, value: float) -> bool:
        if self.__money >= value:
            self.__money -= value
            logger_payment.info("Успешная оплата")
            return True
        logger_payment.warning("Оплата отменена, недостаточно средств")
        if self.__account.guard_sys:
            self.__account.guard_sys.get_warn()
        return False

    def check_account(self, account: Account) -> bool:
        logger_payment.debug("Проверка аккаунта для привязки платёжной системы")
        return self.__account == account


class GuardSystem:
    """
    Система защиты для аккаунта, с помощью неё тоже можно посмотреть на работу WARNING
    Она просто считает предупреждения, которые копятся через get_warn()
    Если получается 3 предупреждения, то отправляется запись о подозрительных действиях
    """

    def __init__(self, account: Account) -> None:
        self.__account = account
        self.__account.guard_sys = self
        self.__warns = 0
        logger_account.info("Успешная регистрация в системе защиты")

    def check_account(self, account: Account) -> bool:
        logger_account.debug("Проверка аккаунта для привязки системы защиты")
        return self.__account == account

    def get_warn(self) -> None:
        self.__warns += 1
        if self.__warns >= 3:
            logger_account.warning(
                "Подозрительная активность в аккаунте %s, требуется сменить пароль",
                self.__account,
            )


def test_db_save():
    try:
        # Имитация ошибки при сохранении
        raise DBSaveException
    except DBSaveException:
        logger_bank.exception(
            "Ошибка при сохранении в БД, текущее подключение к БД было заблокировано"
        )


def test_system():
    try:
        # Имитация системной ошибки
        raise SystemException
    except SystemException as e:
        logger_bank.critical("Произошёл краш при тестовом запуске системы", exc_info=e)
