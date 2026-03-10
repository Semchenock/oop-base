# Bank Project

Учебный проект на Python для работы с банковскими счетами.

## Структура проекта

```
oop-base/
│
├─ src/                    # исходный код
│   └─ accounts/
│       ├─ base.py          # базовый абстрактный аккаунт и исключения
│       ├─ enums.py         # перечисления AccountStatus и AccountCurrency
│       └─ bank_account.py  # класс BankAccount
│
└─ notebooks/              # Jupyter ноутбуки для экспериментов
    └─ day_1.ipynb          # пример использования кода
```

## Возможности

* Создание банковских счетов с уникальным ID
* Поддержка валют: RUB, USD, EUR, KZT, CNY
* Проверка статуса счета (`ACTIVE`, `FROZEN`, `CLOSED`)
* Депозит и снятие средств с проверкой ошибок:

  * `InvalidOperationError` — отрицательные суммы
  * `InsufficientFundsError` — недостаточно средств
  * `AccountFrozenError` / `AccountClosedError` — операции на замороженных/закрытых счетах
* Получение информации о счете (`get_account_info`)
* Красивый вывод счета через `__str__`

## Установка и запуск

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Запуск ноутбука с примерами:

```bash
jupyter notebook notebooks/day_1.ipynb
```
