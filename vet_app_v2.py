import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3


class VetClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система Ветлечебницы")
        self.root.geometry("1150x650")
        self.user_info = ""
        self.show_login_screen()

    def clear_window(self):
        for w in self.root.winfo_children(): w.destroy()

    def show_login_screen(self):
        self.clear_window()
        f = tk.Frame(self.root)
        f.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tk.Label(f, text="Авторизация персонала", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(f, text="Логин:").pack(anchor="w")
        self.entry_user = tk.Entry(f, width=30)
        self.entry_user.pack(pady=5)
        tk.Label(f, text="Пароль:").pack(anchor="w")
        self.entry_pass = tk.Entry(f, show="*", width=30)
        self.entry_pass.pack(pady=5)
        tk.Button(f, text="Войти в систему", command=self.check_login, bg="green", fg="white", width=15).pack(pady=15)

    def check_login(self):
        u, p = self.entry_user.get().strip(), self.entry_pass.get().strip()
        conn = sqlite3.connect('veterinary.db')
        res = conn.execute("SELECT full_name, role FROM staff WHERE username=? AND password=?", (u, p)).fetchone()
        conn.close()
        if res:
            self.user_info = f"{res[0]} ({res[1]})"
            self.show_main_screen()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def show_main_screen(self):
        self.clear_window()
        tb = tk.Frame(self.root, bg="lightgray", height=40)
        tb.pack(fill="x", side="top")
        tk.Label(tb, text=f"Пользователь: {self.user_info}", bg="lightgray", font=("Arial", 10, "bold")).pack(
            side="left", padx=10, pady=10)
        tk.Button(tb, text="Выйти", command=self.show_login_screen, bg="red", fg="white").pack(side="right", padx=10,
                                                                                               pady=5)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True)
        t_pat, t_st, t_calc = ttk.Frame(nb), ttk.Frame(nb), ttk.Frame(nb)
        nb.add(t_pat, text=" Список пациентов ")
        nb.add(t_st, text=" Персонал больницы ")
        nb.add(t_calc, text=" Вычислительный эксперимент ")

        self.setup_crud_tab(t_pat, "patients",
                            ["Кличка", "Вид", "Порода", "Возраст (лет)", "Вес (кг)", "Жалобы", "Особенности",
                             "Состояние"],
                            ("ID", "Кличка", "Вид", "Порода", "Возраст (лет)", "Вес (кг)", "Жалобы", "Особенности",
                             "Состояние"),
                            "INSERT INTO patients VALUES(NULL,?,?,?,?,?,?,?,?)",
                            "UPDATE patients SET pet_name=?, species=?, breed=?, age=?, weight=?, complaints=?, features=?, status=? WHERE id=?")

        self.setup_crud_tab(t_st, "staff", ["Логин", "Пароль", "ФИО Сотрудника", "Должность"],
                            ("ID", "Логин", "Пароль", "ФИО Сотрудника", "Должность"),
                            "INSERT INTO staff VALUES(NULL,?,?,?,?)",
                            "UPDATE staff SET username=?, password=?, full_name=?, role=? WHERE id=?")
        self.load_calc_tab(t_calc)

    def setup_crud_tab(self, frame, table, fields, columns, insert_sql, update_sql):
        mf = tk.Frame(frame)
        mf.pack(fill="both", expand=True, padx=10, pady=10)

        inf = tk.LabelFrame(mf, text=f" Управление ", width=220)
        inf.pack(side="left", fill="y", padx=5, pady=5)
        inf.pack_propagate(False)

        cv = tk.Canvas(inf, borderwidth=0, highlightthickness=0)
        sb = tk.Scrollbar(inf, command=cv.yview)
        sf = tk.Frame(cv)
        sf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0, 0), window=sf, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        entries = {}
        for f in fields:
            tk.Label(sf, text=f + ":").pack(anchor="w", padx=5, pady=2)
            e = ttk.Combobox(sf, values=["Стабильное", "Средняя тяжесть", "Критическое"], width=22,
                             state="readonly") if f == "Состояние" else tk.Entry(sf, width=24)
            e.pack(fill="x", padx=5, pady=2)
            entries[f] = e

        tf = tk.Frame(mf)
        tf.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        tree = ttk.Treeview(tf, columns=columns, show='headings')
        v_sb = tk.Scrollbar(tf, orient="vertical", command=tree.yview)
        h_sb = tk.Scrollbar(tf, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_sb.set, xscrollcommand=h_sb.set)
        for c in columns:
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor=tk.CENTER if c in ["ID", "Возраст (лет)", "Вес (кг)", "Состояние", "Логин",
                                                                "Пароль"] else tk.W)
        v_sb.pack(side="right", fill="y")
        h_sb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            conn = sqlite3.connect('veterinary.db')
            for r in conn.execute(f"SELECT * FROM {table}").fetchall(): tree.insert("", tk.END, values=r)
            conn.close()

        def on_select(e):
            sel = tree.selection()
            if not sel: return
            vals = tree.item(sel, "values")
            for idx, f in enumerate(fields):
                entries[f].set(vals[idx + 1]) if isinstance(entries[f], ttk.Combobox) else (
                    entries[f].delete(0, tk.END), entries[f].insert(0, vals[idx + 1]))

        def save(mode):
            sel = tree.selection()
            if mode != "add" and not sel: return messagebox.showwarning("Внимание", "Выберите запись!")
            vals = [entries[f].get().strip() for f in fields]
            if not vals[0] or not vals[1]: return messagebox.showwarning("Внимание", "Заполните первые два поля!")
            conn = sqlite3.connect('veterinary.db')
            try:
                if mode == "add":
                    conn.execute(insert_sql, vals)
                elif mode == "upd":
                    conn.execute(update_sql, vals + [tree.item(sel, "values")[0]])
                elif mode == "del":
                    if messagebox.askyesno("Удаление", "Удалить запись?"): conn.execute(
                        f"DELETE FROM {table} WHERE id=?", (tree.item(sel, "values")[0],))
                conn.commit()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", "Дубликат данных!")
            conn.close()
            refresh()

        bf = tk.Frame(sf)
        bf.pack(fill="x", pady=10, padx=5)
        tk.Button(bf, text="Добавить", command=lambda: save("add"), bg="blue", fg="white", width=9).grid(row=0,
                                                                                                         column=0,
                                                                                                         padx=2, pady=2)
        tk.Button(bf, text="Сохранить", command=lambda: save("upd"), bg="green", fg="white", width=9).grid(row=0,
                                                                                                           column=1,
                                                                                                           padx=2,
                                                                                                           pady=2)
        tk.Button(bf, text="Удалить", command=lambda: save("del"), bg="red", fg="white").grid(row=1, column=0,
                                                                                              columnspan=2, sticky="we",
                                                                                              padx=2, pady=2)

        tree.bind("<<TreeviewSelect>>", on_select)
        refresh()

    def load_calc_tab(self, frame):
        tf = tk.Frame(frame, pady=10)
        tf.pack(fill="x")
        tk.Label(tf, text="Моделирование доз на основе веса, возраста и рисков состояния животного",
                 font=("Arial", 11, "bold")).pack(side="left", padx=10)
        tk.Button(tf, text="Рассчитать дозировки", command=self.start_experiment, bg="blue", fg="white",
                  font=("Arial", 10, "bold")).pack(side="right", padx=10)
        self.txt_output = tk.Text(frame, font=("Courier", 10), bg="#f5f5f5")
        sb = tk.Scrollbar(frame, command=self.txt_output.yview)
        self.txt_output.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.txt_output.pack(fill="both", expand=True, padx=10, pady=10)

    def start_experiment(self):
        self.txt_output.delete('1.0', tk.END)
        self.txt_output.insert(tk.END, "=== РЕЗУЛЬТАТЫ ВЫЧИСЛИТЕЛЬНОГО ЭКСПЕРИМЕНТА РАСЧЕТА ДОЗ ===\n\n")
        conn = sqlite3.connect('veterinary.db')
        for name, spec, breed, age, w, status, feat in conn.execute(
                "SELECT pet_name, species, breed, age, weight, status, features FROM patients").fetchall():
            dosage = w * (1.2 if spec.lower() == 'кот' else 1.8)
            notes = []
            if age > 8: dosage *= 0.8; notes.append(f"Пожилой возраст ({age} л.) -> коэф. 0.8")
            if status == 'Критическое':
                dosage *= 0.6; notes.append("Критическое состояние -> коэф. 0.6")
            elif status == 'Средняя тяжесть':
                dosage *= 0.85; notes.append("Средняя тяжесть -> коэф. 0.85")
            if feat and ("аллергия" in feat.lower() or "почек" in feat.lower()): dosage *= 0.9; notes.append(
                "Хронические патологии -> коэф. 0.9")
            self.txt_output.insert(tk.END,
                                   f"Кличка: {name} ({spec}, {breed}) | Вес: {w}кг | Итоговая доза: {round(dosage, 2)} мл.\n -> Факторы риска: {'; '.join(notes) if notes else 'Риски отсутствуют (норма)'}\n{'-' * 85}\n")
        conn.close()


if __name__ == '__main__':
    root = tk.Tk()
    app = VetClinicApp(root)
    root.mainloop()
