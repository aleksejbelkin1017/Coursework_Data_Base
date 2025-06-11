import os
import sys
from dotenv import load_dotenv

from src.db_setup import create_database_if_not_exists, create_table_if_not_exists, save_company_to_db, save_vacancies_to_db
from src.api_hh import get_employers_info, get_vacancies_info
from src.db_manager import DBManager


def user_interaction():
    """
    Функция для взаимодействия с пользователем.
    """
    load_dotenv()

    DB_NAME = os.getenv('DATABASE_NAME')
    DB_USER = os.getenv('DATABASE_USER')
    DB_PASS = os.getenv('DATABASE_PASSWORD')

    user_greeting = '\nДобро пожаловать в программу ознакомления с работодателями и их вакансиями!\n'
    print(user_greeting)

    while True:
        question_about_using = input(
            'Хотите ознакомиться с предложениями?\n\nВведите:'
            '\n"1" - для продолжения;'
            '\n"2" - для выхода.\n'
            '\nВы ввели: ')
        if question_about_using == "2":
            print('\nПрограмма завершена!')
            sys.exit()
        elif question_about_using != "1":
            print(f'\nВведено недопустимое значение: "{question_about_using}".\nПопробуйте ещё раз!\n')
        else:
            break

    # Создаём базу данных
    create_database_if_not_exists(DB_NAME, DB_USER, DB_PASS)
    # Создаём таблицу компаний
    create_table_if_not_exists(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host='localhost',
        table_name='employers',
        columns_sql='employer_id VARCHAR(25) PRIMARY KEY, '
                    'employer_name VARCHAR(100) NOT NULL, '
                    'employer_url VARCHAR(255), '
                    'employer_open_vacancy INTEGER')
    # Создаём таблицу вакансий
    create_table_if_not_exists(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host='localhost',
        table_name='vacancies',
        columns_sql='vacancy_id VARCHAR(100) PRIMARY KEY, '
                    'vacancy_name VARCHAR(255), '
                    'employer_name VARCHAR(100) NOT NULL, '
                    'employer_id VARCHAR(25) REFERENCES employers(employer_id), '  
                    'salary_min INTEGER, '
                    'salary_max INTEGER, '
                    'vacancy_url VARCHAR(255), '
                    'requirement_vacancy TEXT')
    # Выгружаем данные по API с HH на основании id компаний и заполняем базу данных
    id_company = [3007832, 6780, 5179427, 10832855, 1684993, 5179890, 4295296, 1840251, 10684958, 4138182, 67611]
    for id_com in id_company:
        # Получаем данные о компаниях
        company_data = get_employers_info(id_com)
        # Наполняем таблицу employers
        save_company_to_db(company_data, 'postgres', '29051989')
        # Получаем данные о вакансиях
        page = 0
        while True:
            vacancies_data = get_vacancies_info(id_com, page)
            if not vacancies_data or 'items' not in vacancies_data or not vacancies_data['items']:
                break
        # Наполняем таблицу vacancies
            save_vacancies_to_db(vacancies_data, 'postgres', '29051989')
            page += 1

    print(f"База данных '{DB_NAME}' готова к использованию!")

    while True:

        db = DBManager(DB_NAME,DB_USER,DB_PASS)

        question_about_vacancies = ('\nВыберете информацию для ознакомления:\n\n'
                                    '"1" - список всех компаний и количество вакансий у каждой компании;\n'
                                    '"2" - список всех вакансий с указанием названия компании, '
                                    'названия вакансии, зарплаты и ссылки на вакансию;\n'
                                    '"3" - средняя зарплата по всем вакансиям в базе данных;\n'
                                    '"4" - список вакансий, зарплата по которым выше средней '
                                    'зарплаты по всем вакансиям;\n'
                                    '"5" - список всех вакансий, в названии которых есть запрашиваемое Вами слово.\n')
        print(question_about_vacancies)
        user_answer_about_vacancies = input('\nВы ввели: ')
        print("-" * 40)

        if user_answer_about_vacancies == "1":
            try:
                db.connect()
                # Код для получения списка всех компаний и количество вакансий у каждой компании
                employers_info = db.get_companies_and_vacancies_count()
                for employer in employers_info:
                    print(f"Компания: {employer['employer_name']}")
                    print(f"Открытых вакансий: {employer['employer_open_vacancy']}\n")
                    print("-" * 40)
            finally:
                db.close()

            while True:
                print('\nЖелаете продолжить работу с базой данных?\n\nВведите:'
                          '\n"1" - Да;'
                          '\n"2" - Нет.\n')
                user_answer_about_next_work = input('\nВы ввели: ')
                if user_answer_about_next_work == "2":
                    print("-" * 40)
                    print('\nПрограмма завершена!')
                    sys.exit()
                elif user_answer_about_next_work != "1":
                    print("-" * 40)
                    print(f'\nВведено недопустимое значение: "{user_answer_about_next_work}".\nПопробуйте ещё раз!')
                else:
                    break

        elif user_answer_about_vacancies == "2":
            try:
                db.connect()
                # Код получает список всех вакансий с указанием названия компании,
                # названия вакансии и зарплаты и ссылки на вакансию
                vacancies_info = db.get_all_vacancies()
                for vacancy in vacancies_info:
                    print(f"Компания: {vacancy['company_name']}")
                    print(f"Вакансия: {vacancy['vacancy_name']}")
                    print(f"Зарплата (мин): {vacancy['salary_min']}")
                    print(f"Зарплата (макс): {vacancy['salary_max']}")
                    print(f"Ссылка: {vacancy['vacancy_url']}")
                    print("-" * 40)
            finally:
                db.close()

            while True:
                print('\nЖелаете продолжить работу с базой данных?\n\nВведите:'
                      '\n"1" - Да;'
                      '\n"2" - Нет.\n')
                user_answer_about_next_work = input('\nВы ввели: ')
                if user_answer_about_next_work == "2":
                    print("-" * 40)
                    print('\nПрограмма завершена!')
                    sys.exit()
                elif user_answer_about_next_work != "1":
                    print("-" * 40)
                    print(f'\nВведено недопустимое значение: "{user_answer_about_next_work}".\nПопробуйте ещё раз!')
                else:
                    break

        elif user_answer_about_vacancies == "3":
            try:
                db.connect()
                # Код получает среднюю зарплату по вакансиям
                avg_salaries = db.get_avg_salary()
                # Выводим результаты
                print(f"\nСредняя минимальная зарплата: {avg_salaries['avg_min']} руб.")
                print(f"Средняя максимальная зарплата: {avg_salaries['avg_max']} руб.")
                print(f"Средняя зарплата: {avg_salaries['avg_salary']} руб.")
                print("-" * 40)
            finally:
                db.close()

            while True:
                print('\nЖелаете продолжить работу с базой данных?\n\nВведите:'
                      '\n"1" - Да;'
                      '\n"2" - Нет.\n')
                user_answer_about_next_work = input('\nВы ввели: ')
                if user_answer_about_next_work == "2":
                    print("-" * 40)
                    print('\nПрограмма завершена!')
                    sys.exit()
                elif user_answer_about_next_work != "1":
                    print("-" * 40)
                    print(f'\nВведено недопустимое значение: "{user_answer_about_next_work}".\nПопробуйте ещё раз!')
                else:
                    break

        elif user_answer_about_vacancies == "4":
            try:
                db.connect()
                # Код получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
                high_salary_vacancies = db.get_vacancies_with_higher_salary()
                # Выводим результаты
                for vacancy in high_salary_vacancies:
                    print(f"Название вакансии: {vacancy['vacancy_name']}")
                    print(f"Описание вакансии: {vacancy['requirement_vacancy']}")
                    print(f"Минимальная зарплата: {vacancy['salary_min']}")
                    print(f"Максимальная зарплата: {vacancy['salary_max']}")
                    # print(f"Средняя зарплата: {vacancy['avg_salary']}")
                    print("-" * 40)
            finally:
                db.close()

            while True:
                print('\nЖелаете продолжить работу с базой данных?\n\nВведите:'
                      '\n"1" - Да;'
                      '\n"2" - Нет.\n')
                user_answer_about_next_work = input('\nВы ввели: ')
                if user_answer_about_next_work == "2":
                    print("-" * 40)
                    print('\nПрограмма завершена!')
                    sys.exit()
                elif user_answer_about_next_work != "1":
                    print("-" * 40)
                    print(f'\nВведено недопустимое значение: "{user_answer_about_next_work}".\nПопробуйте ещё раз!')
                else:
                    break

        elif user_answer_about_vacancies == "5":
            try:
                db.connect()
                user_word = input('\nВведите слово для поиска: ')
                # Поиск вакансий по слову 'python'
                python_vacancies = db.get_vacancies_with_keyword(user_word)
                # Выводим результаты
                for vacancy in python_vacancies:
                    print(f"ID: {vacancy['vacancy_id']}")
                    print(f"Наименование вакансии: {vacancy['vacancy_name']}")
                    print(f"Описание вакансии: {vacancy['requirement_vacancy']}")
                    print(f"Минимальная зарплата: {vacancy['salary_min']}")
                    print(f"Максимальная зарплата: {vacancy['salary_max']}")
                    print("-" * 40)
            finally:
                db.close()

            while True:
                print('\nЖелаете продолжить работу с базой данных?\n\nВведите:'
                      '\n"1" - Да;'
                      '\n"2" - Нет.\n')
                user_answer_about_next_work = input('\nВы ввели: ')
                if user_answer_about_next_work == "2":
                    print("-" * 40)
                    print('\nПрограмма завершена!')
                    sys.exit()
                elif user_answer_about_next_work != "1":
                    print("-" * 40)
                    print(f'\nВведено недопустимое значение: "{user_answer_about_next_work}".\nПопробуйте ещё раз!')
                else:
                    break


if __name__ == '__main__':
    user_interaction()
