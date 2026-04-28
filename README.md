# R4Bot-Module-Profile

Внешний модуль профилей для [R4Bot](https://github.com/Rarmash/R4Bot).

## Что делает
- добавляет `/profile`
- добавляет `/server`
- показывает карточку участника и карточку самого бота
- получает дополнительные поля через profile-provider хуки от других модулей
- использует runtime services из `bot.r4_services`

## Требования
- R4Bot `>= 2.0`
- runtime context с `bot.r4_services`
- сервисы `config`, `firebase`, `module_state`
- настроенные `accent_color` и `admin_id` в `servers.json`

## Особенности
- дополнительные поля не зашиты в модуль по умолчанию и приходят только от установленных модулей
- если данные модули отсутствуют, профиль просто не показывает их поля и не считает это ошибкой

## Структура
- `module.json` — метаданные модуля
- `cog.py` — команды `/profile` и `/server`
- `service.py` — сбор дополнительных полей через provider-хуки
- `requirements.txt` — зависимости для IDE и локальной проверки

## Установка в R4Bot
```powershell
python manage_modules.py install github:Rarmash/R4Bot-Module-Profile@master --enable
```

## Разработка
Для нормальной подсветки импортов в IDE и локальной проверки модуля рекомендуется установить зависимости:

```powershell
python -m pip install -r requirements.txt
```
