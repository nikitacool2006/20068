import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3


class VetClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система Ветлечебницы")
        self.root.geometry("1100x600")

        # Переменная для хранения ФИО вошедшего сотрудника
        self.user_info = ""

        # Сразу показываем экран логина
        self.show_login_screen()

    def show_login_screen(self):
        """Окно авторизации"""
        self.clear_window()

        self.login_frame = tk.Frame(self.root)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(self.login_frame, text="Авторизация персонала", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.login_frame, text="Логин:").pack(anchor=tk.W)
        self.entry_user = tk.Entry(self.login_frame, width=30)
        self.entry_user.pack(pady=5)

        tk.Label(self.login_frame, text="Пароль:").pack(anchor=tk.W)
        self.entry_pass = tk.Entry(self.login_frame, show="*", width=30)
        self.entry_pass.pack(pady=5)

        tk.Button(self.login_frame, text="Войти в систему", command=self.check_login, bg="green", fg="white",
                  width=15).pack(pady=15)

    def check_login(self):
        """Проверка логина и пароля по базе данных"""
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        conn = sqlite3.connect('veterinary.db')
        cursor = conn.cursor()

        # Ищем сотрудника с таким логином и паролем
        cursor.execute("SELECT full_name, role FROM staff WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            self.user_info = f"{result[0]} ({result[1]})"
            self.show_main_screen()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def show_main_screen(self):
        """Главный экран системы после успешного входа"""
        self.clear_window()

        # Верхняя панель пользователя
        top_bar = tk.Frame(self.root, bg="lightgray", height=40)
        top_bar.pack(fill="x", side="top")

        tk.Label(top_bar, text=f"Пользователь: {self.user_info}", bg="lightgray", font=("Arial", 10, "bold")).pack(
            side="left", padx=10, pady=10)
        tk.Button(top_bar, text="Выйти", command=self.show_login_screen, bg="red", fg="white").pack(side="right",
                                                                                                    padx=10, pady=5)

        # Вкладки (Интерфейс со списками и вычислительным экспериментом)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        tab_patients = ttk.Frame(notebook)
        tab_staff = ttk.Frame(notebook)
        tab_calc = ttk.Frame(notebook)

        notebook.add(tab_patients, text=" Список пациентов ")
        notebook.add(tab_staff, text=" Персонал больницы ")
        notebook.add(tab_calc, text=" Вычислительный эксперимент ")

        # Заполнение вкладок данными
        self.load_patients_tab(tab_patients)
        self.load_staff_tab(tab_staff)
        self.load_calc_tab(tab_calc)

    def load_patients_tab(self, frame):
        """Вкладка: Список пациентов клиники"""
        columns = ("ID", "Кличка", "Вид", "Порода", "Возраст (лет)", "Вес (кг)", "Жалобы", "Особенности", "Состояние")
        tree = ttk.Treeview(frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=110,
                        anchor=tk.CENTER if col in ["ID", "Возраст (лет)", "Вес (кг)", "Состояние"] else tk.W)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Берем данные животных из БД
        conn = sqlite3.connect('veterinary.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

    def load_staff_tab(self, frame):
        """Вкладка: Список сотрудников клиники"""
        columns = ("ID", "Логин", "Пароль", "ФИО Сотрудника", "Должность")
        tree = ttk.Treeview(frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180, anchor=tk.CENTER if col in ["ID", "Логин", "Пароль"] else tk.W)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Берем данные сотрудников из БД
        conn = sqlite3.connect('veterinary.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM staff")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
        conn.close()

    def load_calc_tab(self, frame):
        """Вкладка: Математический расчет безопасной дозировки наркоза/препарата"""
        top_frame = tk.Frame(frame, pady=10)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Моделирование доз на основе веса, возраста и рисков состояния животного",
                 font=("Arial", 11, "bold")).pack(side="left", padx=10)
        tk.Button(top_frame, text="Рассчитать дозировки", command=self.start_experiment, bg="blue", fg="white",
                  font=("Arial", 10, "bold")).pack(side="right", padx=10)

        self.txt_output = tk.Text(frame, font=("Courier", 10), bg="#f5f5f5")
        self.txt_output.pack(fill="both", expand=True, padx=10, pady=10)

    def start_experiment(self):
        """Алгоритм вычислительного эксперимента"""
        self.txt_output.delete('1.0', tk.END)
        self.txt_output.insert(tk.END, "=== РЕЗУЛЬТАТЫ ВЫЧИСЛИТЕЛЬНОГО ЭКСПЕРИМЕНТА РАСЧЕТА ДОЗ ===\n\n")

        conn = sqlite3.connect('veterinary.db')
        cursor = conn.cursor()
        cursor.execute("SELECT pet_name, species, breed, age, weight, status, features FROM patients")

        for name, species, breed, age, weight, status, features in cursor.fetchall():
            # Базовая формула расчета: Котам 1.2 мл на кг, собакам 1.8 мл на кг
            rate = 1.2 if species.lower() == 'кот' else 1.8
            dosage = weight * rate

            notes = []
            # Коррекция №1: Пожилые животные (> 8 лет) переносят хуже, дозу снижаем на 20%
            if age > 8:
                dosage *= 0.8
                notes.append(f"Пожилой возраст ({age} л.) -> коэф. 0.8")

            # Коррекция №2: Тяжесть клинического состояния
            if status == 'Критическое':
                dosage *= 0.6
                notes.append("Критическое состояние -> коэф. 0.6")
            elif status == 'Средняя тяжесть':
                dosage *= 0.85
                notes.append("Средняя тяжесть -> коэф. 0.85")

            # Коррекция №3: Патологии органов или аллергии в анамнезе
            if "аллергия" in features.lower() or "почек" in features.lower():
                dosage *= 0.9
                notes.append("Хронические патологии -> коэф. 0.9")

            final_dose = round(dosage, 2)
            risk_info = "; ".join(notes) if notes else "Риски отсутствуют (норма)"

            # Выводим строку в текстовое поле программы
            result_line = f"Кличка: {name} ({species}, {breed}) | Вес: {weight}кг | Итоговая доза: {final_dose} мл.\n -> Факторы риска: {risk_info}\n{'-' * 85}\n"
            self.txt_output.insert(tk.END, result_line)

        conn.close()

    def clear_window(self):
        """Очистка всех элементов с экрана при смене окон"""
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = VetClinicApp(root)
    root.mainloop()
