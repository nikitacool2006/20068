import sqlite3
import sys

def login():
    print("=== АВТОРИЗАЦИЯ ВРАЧА (Версия 1) ===")
    username = input("Логин: ")
    password = input("Пароль: ")
    
    conn = sqlite3.connect('veterinary.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE username=? AND password=?", (username, password))
    doctor = cursor.fetchone()
    conn.close()
    
    if doctor:
        print(f"\nДобро пожаловать, {doctor[3]} ({doctor[4]})!")
        return True
    else:
        print("Ошибка: Неверный логин или пароль!")
        return False

def calculate_dosage(species, weight):
    # Вычислительный эксперимент v1: базовый расчет дозы на 1 кг веса
    base_rate = 1.5 if species.lower() == 'кот' else 2.0
    return round(weight * base_rate, 2)

def main_menu():
    while True:
        print("\n--- Меню системы ---")
        print("1. Просмотр списка пациентов")
        print("2. Добавить пациента")
        print("3. Вычислительный эксперимент (Расчет дозировки)")
        print("4. Выход")
        choice = input("Выберите действие: ")
        
        conn = sqlite3.connect('veterinary.db')
        cursor = conn.cursor()
        
        if choice == '1':
            cursor.execute("SELECT * FROM patients")
            for p in cursor.fetchall():
                print(f"ID: {p[0]} | Кличка: {p[1]} | Вид: {p[2]} | Возраст: {p[3]} | Владелец: {p[4]} | Диагноз: {p[5]} | Вес: {p[6]}кг")
        elif choice == '2':
            name = input("Кличка: ")
            spec = input("Вид (Кот/Собака): ")
            age = int(input("Возраст (лет): "))
            owner = input("ФИО владельца: ")
            diag = input("Диагноз: ")
            weight = float(input("Вес (кг): "))
            cursor.execute("INSERT INTO patients (pet_name, species, age, owner_name, diagnosis, weight) VALUES (?, ?, ?, ?, ?, ?)",
                           (name, spec, age, owner, diag, weight))
            conn.commit()
            print("Пациент добавлен!")
        elif choice == '3':
            cursor.execute("SELECT id, pet_name, species, weight FROM patients")
            patients = cursor.fetchall()
            for p in patients:
                dosage = calculate_dosage(p[2], p[3])
                print(f"Питомец: {p[1]} ({p[2]}), Вес: {p[3]}кг -> Рекомендуемая доза: {dosage} мл.")
        elif choice == '4':
            conn.close()
            sys.exit()
        conn.close()

if __name__ == '__main__':
    if login():
        main_menu()
