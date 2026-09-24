"""
Главный модуль, который запускает всю логику из bank.py
Здесь можно потестировать код из bank.py и посмотреть,
как отработает система логирования
"""

from bank import (
    Account,
    GuardSystem,
    PaymentSystem,
    test_db_save,
    test_system,
)

new_acc = Account("Vlad", "demo-password")
new_pay_sys = PaymentSystem(new_acc)
new_guard_sys = GuardSystem(new_acc)
vlad_acc = Account.log_in("Wald", "password")
vlad_acc = Account.log_in("Vlad", "password")
vlad_acc = Account.log_in("Vlad", "demo-password")
stealer = Account("hack", "robber")
if vlad_acc:
    vlad_acc.pay_sys = PaymentSystem(stealer)
new_pay_sys.pay(500)
new_pay_sys.pay(600)
test_db_save()
test_system()
print("Логи записаны. Проверь файл modules/app-YYYY-MM-DD.log")
