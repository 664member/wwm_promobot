<<<<<<< HEAD
=======
# WWm PromoBot

Автоматический ввод промокодов в игру через эмуляцию кликов и клавиатуры. Работает с любым разрешением и несколькими мониторами — координаты настраиваются вручную через `F2`.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Возможности

- **Три клика на промо** — открыть меню → фокус на поле → подтвердить.
- **Детект результата по цвету пикселя** — не нужен OCR. Успех = меню закрылось само, ошибка = меню осталось с затемнением.
- **Независимость от раскладки** — ввод через `keyboard.write()` (скан-коды, а не символы).
- **Пропуск уже использованных и ошибочных промо** — раздельные файлы `used_promos.txt` и `failed_promos.txt`.
- **Дедупликация** — одинаковые промо из `promos.txt` не вводятся дважды за запуск.
- **Автоматическая страховка** — если меню с прошлой итерации подвисло, бот закроет его перед следующим промо.
- **GUI** — прогресс-бар, счётчики успехов/ошибок/пропусков и строка текущего промо.
- **Остановка по F5** — глобальный хоткей, работает даже когда фокус в игре.
- **Настройка через CLI** — все координаты, задержки и допуски задаются один раз.

---

## 📋 Требования

- **Windows** (используется `pyautogui`, `keyboard`, `tkinter`).
- **Python 3.10 – 3.12**. На 3.13+ возможны проблемы с `Pillow`/`pyscreeze` — если `pyautogui.pixel()` падает, перейди на 3.12.
- Игра должна быть запущена **от того же уровня привилегий**, что и Python (если игра от админа — запускай терминал от админа).

---

>>>>>>> b5ffed94eaea750e4635b6e467788b10e30c2bf9
## 🚀 Установка

```powershell
# 1. Клонируй репозиторий
<<<<<<< HEAD
git clone https://github.com/664member/wwm_promobot.git
cd wwm_promobot

# 2. Создай виртуальное окружение на Python 3.12
=======
git clone https://github.com/664Mmember/wwm_promobot.git
cd wwm-promobot

# 2. Создай виртуальное окружение (рекомендуется)
>>>>>>> b5ffed94eaea750e4635b6e467788b10e30c2bf9
py -3.12 -m venv venv
.\venv\Scripts\activate

# 3. Установи зависимости
pip install pyautogui keyboard pillow
<<<<<<< HEAD
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
=======
>>>>>>> b5ffed94eaea750e4635b6e467788b10e30c2bf9
