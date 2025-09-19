#  ollama_manager.py
"""
Ollama Manager (Windows GUI)

Приложение на Python + Tkinter для управления локальными моделями Ollama.

Функции:
- Отображение списка установленных моделей (`ollama list`)
- Запуск выбранной модели (`ollama run <model>`)
- Остановка выбранной модели (`ollama stop <model>`)
- Остановка всех моделей (`ollama stop all`)
- Просмотр активных моделей (`ollama ps`)

Интерфейс:
- Выпадающий список (ComboBox) с установленными моделями
- Кнопки: Обновить список, Запустить, Остановить, Остановить все, Активные
- Текстовое поле для вывода логов и статуса команд

Требования:
- Python 3.x
- Установленный Ollama (ollama.exe в PATH)
- Tkinter (идёт в стандартной библиотеке Python)
"""

import tkinter as tk
from tkinter import messagebox, ttk
import subprocess


def run_cmd(cmd: str) -> str:
    """Запуск shell-команды и возврат результата"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)


def refresh_models():
    """Обновить список моделей"""
    output = run_cmd("ollama list")
    lines = output.strip().splitlines()
    models = []

    # пропускаем шапку "NAME ID SIZE MODIFIED"
    for line in lines[1:]:
        parts = line.split()
        if parts:
            models.append(parts[0])  # первая колонка — имя модели

    combo_models["values"] = models
    if models:
        combo_models.current(0)  # выбрать первую модель
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, output)


def run_model():
    """Запуск выбранной модели"""
    model = combo_models.get()
    if not model:
        messagebox.showwarning("Ошибка", "Выберите модель")
        return
    output = run_cmd(f"ollama run {model}")
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, output)


def stop_model():
    """Остановить выбранную модель"""
    model = combo_models.get()
    if not model:
        messagebox.showwarning("Ошибка", "Выберите модель")
        return
    output = run_cmd(f"ollama stop {model}")
    messagebox.showinfo("Stop model", output if output else f"Модель {model} остановлена")


def stop_all():
    """Остановить все модели"""
    output = run_cmd("ollama stop all")
    messagebox.showinfo("Stop all", output if output else "Все модели остановлены")


def ps_models():
    """Показать активные модели"""
    output = run_cmd("ollama ps")
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, output)


# GUI окно
root = tk.Tk()
root.title("Ollama Manager")

frame = tk.Frame(root)
frame.pack(pady=10)

# Выпадающий список моделей
combo_models = ttk.Combobox(frame, width=40)
combo_models.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

btn_refresh = tk.Button(frame, text="Обновить список", command=refresh_models, width=20)
btn_refresh.grid(row=1, column=0, padx=5, pady=5)

btn_run = tk.Button(frame, text="Запустить", command=run_model, width=20)
btn_run.grid(row=1, column=1, padx=5, pady=5)

btn_stop = tk.Button(frame, text="Остановить", command=stop_model, width=20)
btn_stop.grid(row=2, column=0, padx=5, pady=5)

btn_stop_all = tk.Button(frame, text="Остановить все", command=stop_all, width=20)
btn_stop_all.grid(row=2, column=1, padx=5, pady=5)

btn_ps = tk.Button(frame, text="Активные", command=ps_models, width=20)
btn_ps.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

text_output = tk.Text(root, height=20, width=80)
text_output.pack(pady=10)

# Автоподгрузка списка при старте
refresh_models()

root.mainloop()
