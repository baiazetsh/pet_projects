import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from collections import defaultdict
import calendar

class DiabetesTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник диабетика")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.data_file = "glucose_data.json"
        self.records = self.load_data()
        
        self.create_widgets()
        self.update_records_list()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        # Верхняя панель для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        ttk.Label(input_frame, text="Дата:").grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=0, column=1, padx=5)
        
        # Время
        ttk.Label(input_frame, text="Время:").grid(row=0, column=2, sticky="w", padx=5)
        self.time_entry = ttk.Entry(input_frame, width=10)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.grid(row=0, column=3, padx=5)
        
        # Уровень сахара
        ttk.Label(input_frame, text="Сахар (ммоль/л):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.glucose_entry = ttk.Entry(input_frame, width=15)
        self.glucose_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить", command=self.add_record).grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        # Список записей
        records_frame = ttk.LabelFrame(self.root, text="История измерений", padding=10)
        records_frame.pack(fill="both", expand=False, padx=10, pady=5)
        
        # Таблица
        columns = ("Дата", "Время", "Сахар")
        self.tree = ttk.Treeview(records_frame, columns=columns, show="headings", height=8)
        
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Время", text="Время")
        self.tree.heading("Сахар", text="Сахар (ммоль/л)")
        
        self.tree.column("Дата", width=100)
        self.tree.column("Время", width=80)
        self.tree.column("Сахар", width=120)
        
        scrollbar = ttk.Scrollbar(records_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка удаления
        ttk.Button(records_frame, text="Удалить выбранную запись", command=self.delete_record).pack(pady=5)
        
        # Панель графиков
        graph_frame = ttk.LabelFrame(self.root, text="Графики", padding=10)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Кнопки для графиков
        btn_frame = ttk.Frame(graph_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Все время", command=lambda: self.show_graph("all")).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="По месяцам", command=lambda: self.show_graph("month")).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="По годам", command=lambda: self.show_graph("year")).pack(side="left", padx=5)
        
        # Область для графика
        self.graph_container = ttk.Frame(graph_frame)
        self.graph_container.pack(fill="both", expand=True)
        
    def add_record(self):
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        glucose_str = self.glucose_entry.get().strip()
        
        try:
            # Проверка даты
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            # Проверка времени
            time_obj = datetime.strptime(time_str, "%H:%M")
            # Проверка уровня сахара
            glucose = float(glucose_str.replace(',', '.'))
            
            if glucose <= 0:
                raise ValueError("Уровень сахара должен быть положительным")
            
            record = {
                "date": date_str,
                "time": time_str,
                "glucose": glucose,
                "datetime": f"{date_str} {time_str}"
            }
            
            self.records.append(record)
            self.records.sort(key=lambda x: datetime.strptime(x["datetime"], "%d.%m.%Y %H:%M"), reverse=True)
            self.save_data()
            self.update_records_list()
            
            # Очистка поля сахара
            self.glucose_entry.delete(0, tk.END)
            messagebox.showinfo("Успех", "Запись добавлена!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных!\nДата: ДД.ММ.ГГГГ\nВремя: ЧЧ:ММ\nСахар: число\n\n{str(e)}")
    
    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            item = self.tree.item(selected[0])
            values = item['values']
            
            # Находим и удаляем запись
            for i, record in enumerate(self.records):
                if record['date'] == values[0] and record['time'] == values[1] and record['glucose'] == values[2]:
                    self.records.pop(i)
                    break
            
            self.save_data()
            self.update_records_list()
            messagebox.showinfo("Успех", "Запись удалена")
    
    def update_records_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for record in self.records:
            self.tree.insert("", "end", values=(record['date'], record['time'], record['glucose']))
    
    def show_graph(self, period):
        if not self.records:
            messagebox.showinfo("Информация", "Нет данных для отображения")
            return
        
        # Очистка предыдущего графика
        for widget in self.graph_container.winfo_children():
            widget.destroy()
        
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        if period == "all":
            self.plot_all_time(ax)
        elif period == "month":
            self.plot_by_month(ax)
        elif period == "year":
            self.plot_by_year(ax)
        
        canvas = FigureCanvasTkAgg(fig, self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def plot_all_time(self, ax):
        dates = []
        values = []
        
        for record in sorted(self.records, key=lambda x: datetime.strptime(x["datetime"], "%d.%m.%Y %H:%M")):
            dt = datetime.strptime(record["datetime"], "%d.%m.%Y %H:%M")
            dates.append(dt)
            values.append(record["glucose"])
        
        ax.plot(dates, values, marker='o', linestyle='-', linewidth=2, markersize=6)
        ax.set_xlabel("Дата", fontsize=10)
        ax.set_ylabel("Уровень сахара (ммоль/л)", fontsize=10)
        ax.set_title("История измерений", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=5.5, color='g', linestyle='--', alpha=0.5, label='Норма')
        ax.axhline(y=7.0, color='orange', linestyle='--', alpha=0.5, label='Повышенный')
        ax.legend()
        fig.autofmt_xdate()
    
    def plot_by_month(self, ax):
        monthly_data = defaultdict(list)
        
        for record in self.records:
            dt = datetime.strptime(record["date"], "%d.%m.%Y")
            month_key = dt.strftime("%m.%Y")
            monthly_data[month_key].append(record["glucose"])
        
        months = sorted(monthly_data.keys(), key=lambda x: datetime.strptime(x, "%m.%Y"))
        avg_values = [sum(monthly_data[m]) / len(monthly_data[m]) for m in months]
        
        month_labels = [datetime.strptime(m, "%m.%Y").strftime("%b %Y") for m in months]
        
        ax.bar(range(len(months)), avg_values, color='steelblue', alpha=0.7)
        ax.set_xlabel("Месяц", fontsize=10)
        ax.set_ylabel("Средний уровень сахара (ммоль/л)", fontsize=10)
        ax.set_title("Средние показатели по месяцам", fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(month_labels, rotation=45, ha='right')
        ax.axhline(y=5.5, color='g', linestyle='--', alpha=0.5, label='Норма')
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend()
    
    def plot_by_year(self, ax):
        yearly_data = defaultdict(list)
        
        for record in self.records:
            dt = datetime.strptime(record["date"], "%d.%m.%Y")
            year = dt.year
            yearly_data[year].append(record["glucose"])
        
        years = sorted(yearly_data.keys())
        avg_values = [sum(yearly_data[y]) / len(yearly_data[y]) for y in years]
        
        ax.bar(years, avg_values, color='coral', alpha=0.7, width=0.6)
        ax.set_xlabel("Год", fontsize=10)
        ax.set_ylabel("Средний уровень сахара (ммоль/л)", fontsize=10)
        ax.set_title("Средние показатели по годам", fontsize=12, fontweight='bold')
        ax.axhline(y=5.5, color='g', linestyle='--', alpha=0.5, label='Норма')
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiabetesTracker(root)
    root.mainloop()