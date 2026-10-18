import os
import json
import time
import threading
import queue
import tkinter as tk
from tkinter import ttk
from pathlib import Path

import pyautogui
import keyboard

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
PROMOS_FILE = BASE_DIR / "promos.txt"
USED_FILE = BASE_DIR / "used_promos.txt"
FAILED_FILE = BASE_DIR / "failed_promos.txt"


# ---------- Конфигурация ----------
def load_config():
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠ config.json повреждён ({e}), начинаю с чистого листа.")
        return {}


def save_config(cfg):
    tmp = CONFIG_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, CONFIG_FILE)


# ---------- Ввод через F2 ----------
def capture_point(name):
    print(f"\n[{name}] Наведи мышь на нужное место и нажми F2...")
    while True:
        if keyboard.is_pressed("f2"):
            x, y = pyautogui.position()
            while keyboard.is_pressed("f2"):
                time.sleep(0.05)
            print(f"  → Сохранено: ({x}, {y})")
            return [x, y]
        time.sleep(0.05)


def wait_f2(message):
    print(message)
    while True:
        if keyboard.is_pressed("f2"):
            while keyboard.is_pressed("f2"):
                time.sleep(0.05)
            break
        time.sleep(0.05)


# ---------- Настройка ----------
def setup_coordinates():
    print("=" * 50)
    print("НАСТРОЙКА КООРДИНАТ")
    print("=" * 50)
    print("F2 — зафиксировать позицию мыши / подтвердить действие")
    print("=" * 50)

    cfg = load_config()
    cfg["menu_button"] = capture_point("Кнопка открытия меню с инпутом")
    cfg["input_field"] = capture_point("Поле ввода промокода")
    cfg["submit_button"] = capture_point("Кнопка подтверждения (конфирм)")

    print("\n[Эталон цвета] Убедись, что меню с инпутом в игре ЗАКРЫТО.")
    wait_f2("  Когда меню закрыто — нажми F2...")
    time.sleep(0.2)
    cfg["closed_menu_color"] = list(pyautogui.pixel(*cfg["menu_button"]))
    print(f"  → Эталонный цвет кнопки меню: {tuple(cfg['closed_menu_color'])}")

    print("\nНастройка задержек (в секундах, Enter = значение по умолчанию):")
    cfg["delay_after_input"] = float(input("  Задержка после клика/ввода [0.5]: ") or 0.5)
    cfg["delay_after_submit"] = float(input("  Задержка перед первой проверкой цвета [1.5]: ") or 1.5)
    cfg["delay_between_promos"] = float(input("  Задержка между промо [2.0]: ") or 2.0)

    cfg["color_tolerance"] = int(input("  Допуск по цвету RGB [25]: ") or 25)

    cfg["color_check_attempts"] = int(
        input("  Сколько раз перепроверять цвет, если меню не закрылось [3]: ") or 3
    )
    cfg["color_check_interval"] = float(
        input("  Интервал между перепроверками, сек [0.5]: ") or 0.5
    )

    ans = input("\nПропускать ранее использованные промо? (y/n) [y]: ").strip().lower()
    cfg["skip_used"] = ans != "n"

    save_config(cfg)
    print("\n✓ Конфигурация сохранена в", CONFIG_FILE)

    ans = input("\nПроверить детект цвета сейчас? (y/n) [y]: ").strip().lower()
    if ans != "n":
        wait_f2("  Открой меню в игре, затем нажми F2...")
        time.sleep(0.2)
        open_color = tuple(pyautogui.pixel(*cfg["menu_button"]))
        wait_f2("  Закрой меню, затем нажми F2...")
        time.sleep(0.2)
        closed_color = tuple(pyautogui.pixel(*cfg["menu_button"]))
        diff = color_distance(open_color, closed_color)
        print(f"  Цвет открытого меню: {open_color}")
        print(f"  Цвет закрытого меню: {closed_color}")
        print(f"  Разница: {diff} (должна быть >> допуска {cfg['color_tolerance']})")
        if diff > cfg["color_tolerance"] * 2:
            print("  ✓ Детект должен работать нормально.")
        else:
            print("  ⚠ Разница слишком маленькая — возможно, точка выбрана неудачно.")


# ---------- Утилиты ----------
def click_at(pos):
    pyautogui.click(pos[0], pos[1])


def get_pixel_color(pos):
    return pyautogui.pixel(pos[0], pos[1])


def color_distance(c1, c2):
    return max(abs(c1[0] - c2[0]), abs(c1[1] - c2[1]), abs(c1[2] - c2[2]))


def clear_input(cfg):
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.05)
    pyautogui.press("backspace")
    time.sleep(0.05)
    for _ in range(3):
        pyautogui.press("backspace")
        time.sleep(0.02)


def type_text(text):
    """Ввод текста независимо от раскладки."""
    keyboard.write(text, delay=0.05)


def read_promos_raw():
    """Читает все строки из promos.txt как есть (с дублями, пустые отбрасываются)."""
    if not PROMOS_FILE.exists():
        return []
    with open(PROMOS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def _read_file_to_set(path):
    if not path.exists():
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def read_skip_set():
    """Объединяет used_promos.txt и failed_promos.txt — всё это пропускается."""
    return _read_file_to_set(USED_FILE) | _read_file_to_set(FAILED_FILE)


def append_used(promo):
    with open(USED_FILE, "a", encoding="utf-8") as f:
        f.write(promo + "\n")


def append_failed(promo):
    with open(FAILED_FILE, "a", encoding="utf-8") as f:
        f.write(promo + "\n")


# ---------- Основная логика ----------
def wait_for_menu_close(ref, closed_color, tol, attempts, interval, stop_event):
    for n in range(1, attempts + 1):
        if stop_event.is_set():
            return False
        now_color = get_pixel_color(ref)
        dist = color_distance(closed_color, now_color)
        if dist <= tol:
            return True
        if n < attempts:
            time.sleep(interval)
    return False


def activate_promo(promo, cfg, stop_event):
    ref = tuple(cfg["menu_button"])
    tol = cfg["color_tolerance"]
    attempts = cfg.get("color_check_attempts", 3)
    interval = cfg.get("color_check_interval", 0.5)
    closed_color = tuple(cfg["closed_menu_color"])

    # 1. Проверка подвисшего меню
    current_color = get_pixel_color(ref)
    if color_distance(closed_color, current_color) > tol:
        click_at(cfg["menu_button"])
        pyautogui.moveTo(5, 5)
        time.sleep(cfg["delay_after_input"])
        time.sleep(cfg["delay_after_input"])

    if stop_event.is_set():
        return "error"

    # 2. Клик 1 — открыть меню
    click_at(cfg["menu_button"])
    pyautogui.moveTo(5, 5)
    time.sleep(cfg["delay_after_input"])

    if stop_event.is_set():
        return "error"

    # 3. Клик 2 — фокус на поле ввода
    click_at(cfg["input_field"])
    time.sleep(0.2)

    # 4. Очистка + ввод
    clear_input(cfg)
    type_text(promo)
    time.sleep(cfg["delay_after_input"])

    if stop_event.is_set():
        return "error"

    # 5. Клик 3 — подтвердить
    click_at(cfg["submit_button"])

    # 6. Ждём закрытия меню
    time.sleep(cfg["delay_after_submit"])
    if wait_for_menu_close(ref, closed_color, tol, attempts, interval, stop_event):
        return "success"

    return "error"


# ---------- GUI ----------
class BotApp:
    def __init__(self, root, cfg):
        self.root = root
        self.cfg = cfg
        self.stop_event = threading.Event()
        self.worker = None
        self.result_queue = queue.Queue()

        self.root.title("WWm PromoBot")
        self.root.geometry("480x220")
        self.root.attributes("-topmost", True)

        # --- Статистика ---
        stats_frame = tk.LabelFrame(root, text="Статистика", padx=8, pady=8)
        stats_frame.pack(fill="x", padx=10, pady=8)

        self.total_var = tk.StringVar(value="Всего строк: 0")
        self.dupe_var = tk.StringVar(value="Дубликатов: 0")
        self.skip_var = tk.StringVar(value="Пропущено: 0")
        self.success_var = tk.StringVar(value="Успех: 0")
        self.error_var = tk.StringVar(value="Ошибка: 0")

        tk.Label(stats_frame, textvariable=self.total_var, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(stats_frame, textvariable=self.success_var, anchor="w", fg="green").grid(row=0, column=1, sticky="w", padx=15)
        tk.Label(stats_frame, textvariable=self.dupe_var, anchor="w", fg="gray").grid(row=1, column=0, sticky="w")
        tk.Label(stats_frame, textvariable=self.skip_var, anchor="w", fg="gray").grid(row=1, column=1, sticky="w", padx=15)
        tk.Label(stats_frame, textvariable=self.error_var, anchor="w", fg="red").grid(row=2, column=0, sticky="w")

        # --- Прогресс ---
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=6)

        self.current_var = tk.StringVar(value="Подготовка...")
        tk.Label(root, textvariable=self.current_var, anchor="w").pack(fill="x", padx=10)

        hint = tk.Label(root, text="F5 — остановка", fg="gray")
        hint.pack(side="bottom", anchor="e", padx=10, pady=4)

        keyboard.add_hotkey("f5", self.stop)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Автостарт
        self.root.after(200, self.start)

    def start(self):
        if self.worker and self.worker.is_alive():
            return
        self.stop_event.clear()
        self.current_var.set("Старт через 5 сек... переключись в игру")
        self.worker = threading.Thread(target=self.run_bot, daemon=True)
        self.worker.start()

    def stop(self):
        if not self.stop_event.is_set():
            self.stop_event.set()
            self.result_queue.put(("current", "Остановка..."))

    def on_close(self):
        self.stop_event.set()
        keyboard.unhook_all_hotkeys()
        self.root.destroy()

    # ---------- Работа бота ----------
    def run_bot(self):
        cfg = self.cfg
        raw = read_promos_raw()
        skip = read_skip_set() if cfg.get("skip_used") else set()

        if not raw:
            self.result_queue.put(("current", "✗ Список промо пуст"))
            self.result_queue.put(("finish", None))
            return

        total_lines = len(raw)

        # Дедупликация
        seen = set()
        unique = []
        for p in raw:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        dupes = total_lines - len(unique)

        self.result_queue.put(("total", total_lines))
        self.result_queue.put(("stats", (total_lines, dupes, 0, 0, 0)))

        # Отсчёт
        for n in range(5, 0, -1):
            if self.stop_event.is_set():
                self.result_queue.put(("finish", None))
                return
            self.result_queue.put(("current", f"Старт через {n}... переключись в игру"))
            time.sleep(1)

        success = 0
        errors = []
        skipped = 0
        processed = 0
        seen_in_run = set()

        for promo in unique:
            if self.stop_event.is_set():
                break

            occurrences = raw.count(promo)

            # Пропуск: уже в used/failed, или уже вводили в этом прогоне
            if promo in skip or promo in seen_in_run:
                skipped += occurrences
                processed += occurrences
                self.result_queue.put(("progress", processed))
                self.result_queue.put(("stats", (total_lines, dupes, skipped, success, len(errors))))
                continue

            seen_in_run.add(promo)

            self.result_queue.put((
                "current",
                f"[{processed + 1}/{total_lines}] Ввожу: {promo}"
            ))

            try:
                result = activate_promo(promo, cfg, self.stop_event)
            except Exception as e:
                print(f"  ✗ Исключение на {promo}: {e}")
                result = "error"

            if result == "success":
                success += occurrences
                if cfg.get("skip_used"):
                    append_used(promo)
            else:
                errors.extend([promo] * occurrences)
                if cfg.get("skip_used"):
                    append_failed(promo)   # <-- ошибки тоже в скип

            processed += occurrences
            self.result_queue.put(("progress", processed))
            self.result_queue.put(("stats", (total_lines, dupes, skipped, success, len(errors))))

            # Пауза с проверкой F5
            elapsed = 0.0
            while elapsed < cfg["delay_between_promos"]:
                if self.stop_event.is_set():
                    break
                time.sleep(0.1)
                elapsed += 0.1

        self.result_queue.put((
            "current",
            f"Готово: успех {success}, ошибок {len(errors)}, пропущено {skipped}"
        ))
        self.result_queue.put(("finish", None))

    # ---------- Опрос очереди ----------
    def poll_queue(self):
        try:
            while True:
                kind, data = self.result_queue.get_nowait()
                if kind == "total":
                    self.progress.configure(maximum=data)
                    self.total_var.set(f"Всего строк: {data}")
                elif kind == "stats":
                    total, dupes, skipped, success, err = data
                    self.total_var.set(f"Всего строк: {total}")
                    self.dupe_var.set(f"Дубликатов: {dupes}")
                    self.skip_var.set(f"Пропущено: {skipped}")
                    self.success_var.set(f"Успех: {success}")
                    self.error_var.set(f"Ошибка: {err}")
                elif kind == "progress":
                    self.progress.configure(value=data)
                elif kind == "current":
                    self.current_var.set(data)
                elif kind == "finish":
                    pass
        except queue.Empty:
            pass
        self.root.after(100, self.poll_queue)


def main_gui():
    cfg = load_config()
    if not cfg or "menu_button" not in cfg or "closed_menu_color" not in cfg:
        print("✗ Конфигурация не найдена или неполная.")
        print("  Запусти: python bot.py --setup")
        return

    root = tk.Tk()
    app = BotApp(root, cfg)
    app.poll_queue()
    root.mainloop()


# ---------- CLI ----------
if __name__ == "__main__":
    import sys

    if "--setup" in sys.argv:
        setup_coordinates()
    elif "--reset" in sys.argv:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
            print("✓ Конфигурация сброшена.")
    elif "--clear-used" in sys.argv:
        cleared = []
        if USED_FILE.exists():
            USED_FILE.unlink()
            cleared.append(USED_FILE.name)
        if FAILED_FILE.exists():
            FAILED_FILE.unlink()
            cleared.append(FAILED_FILE.name)
        if cleared:
            print("✓ Очищено:", ", ".join(cleared))
        else:
            print("ℹ Нечего очищать — файлов истории нет.")
    else:
        main_gui()