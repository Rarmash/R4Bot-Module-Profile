# R4Bot-Module-Profile

Внешний модуль профилей для [R4Bot](https://github.com/Rarmash/R4Bot).

## Что делает
- добавляет `/profile`
- показывает карточку участника и карточку самого бота
- автоматически скрывает игровые и статистические поля, если соответствующие модули не установлены или выключены
- получает дополнительные игровые поля через profile extensions от других модулей
- использует runtime services из `bot.r4_services`

## Требования
- R4Bot `>= 2.0`
- runtime context с `bot.r4_services`
- сервисы `config`, `firebase`, `module_state`, `profile_extensions`
- настроенные `accent_color` и `admin_id` в `servers.json`

## Особенности
- поля `Сообщений`, `Тайм-аутов` и `Голосовой активности` показываются только если включены соответствующие модули
- игровые поля не зашиты в модуль по умолчанию и приходят только от установленных игровых модулей

## Структура
- `module.json` — метаданные модуля
- `cog.py` — Discord cog
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
