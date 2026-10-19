## 🚀 Установка

```powershell
# 1. Клонируй репозиторий
git clone https://github.com/664member/wwm_promobot.git
cd wwm_promobot

# 2. Создай виртуальное окружение на Python 3.12
py -3.12 -m venv venv
.\venv\Scripts\activate

# 3. Установи зависимости
pip install pyautogui keyboard pillow
```

> ⚠️ **Важно.** Проект нужно запускать **строго из `venv` на Python 3.12**. На Python 3.13+ (а тем более 3.15 alpha) `pyautogui.pixel()` падает с ошибкой `PyAutoGUI was unable to import pyscreeze`, потому что `Pillow` не поддерживает эти версии.

---

## ▶️ Запуск

### Вариант 1 — через `run.bat` (рекомендуется)

В корне проекта лежит `run.bat`. Он сам активирует `venv` и запускает бота:

```bat
@echo off
call "%~dp0venv\Scripts\activate.bat"
python "%~dp0bot.py"
pause
```

Просто **дважды кликни по `run.bat`** — откроется окно бота с правильной версией Python. Ничего настраивать вручную не нужно.

### Вариант 2 — вручную из терминала

```powershell
.\venv\Scripts\activate
python bot.py
```

В начале строки терминала должно появиться `(venv)`. Если его нет — ты запускаешь глобальный Python, и бот упадёт с ошибкой `pyscreeze`.

### Вариант 3 — через VS Code

1. `Ctrl+Shift+P` → `Python: Select Interpreter`.
2. Выбери `.\venv\Scripts\python.exe`.
3. Запускай `bot.py` через `F5` или кнопку Run — VS Code будет использовать правильный интерпретатор.

### CLI-команды

```powershell
python bot.py              # запуск GUI
python bot.py --setup      # настройка координат и задержек
python bot.py --reset      # сбросить config.json
python bot.py --clear-used # очистить used_promos.txt и failed_promos.txt
```