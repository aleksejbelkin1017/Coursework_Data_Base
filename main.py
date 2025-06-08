from src.db_setup import create_database_if_not_exists, create_table_if_not_exists, save_company_to_db
from src.api_hh import get_employers_info

def user_interaction():
    # Создаём базу данных
    create_database_if_not_exists(
        'employers_vacations_database',
        'postgres',
        '29051989')
    #print('База данных успешно создана.')

    # Создаём таблицу компаний
    create_table_if_not_exists(
        dbname='employers_vacations_database',
        user='postgres',
        password='29051989',
        host='localhost',
        table_name='employers',
        columns_sql='employer_id VARCHAR(25) PRIMARY KEY, '
                    'employer_name VARCHAR(100) NOT NULL, '
                    'employer_url VARCHAR(255), '
                    'employer_open_vacancy INTEGER')

    # Создаём таблицу вакансий
    create_table_if_not_exists(
        dbname='employers_vacations_database',
        user='postgres',
        password='29051989',
        host='localhost',
        table_name='vacancies',  # Изменено имя таблицы
        columns_sql='vacancy_id SERIAL PRIMARY KEY, '
                    'company_name VARCHAR(100) NOT NULL, '
                    'company_id VARCHAR(25) REFERENCES employers(employer_id), '  # Добавлена связь с таблицей company
                    'salary_min INTEGER, '
                    'salary_max INTEGER'

    )


    # Выгружаем данные по API с HH на основании id компаний
    id_company = [3007832, 6780, 5179427, 10832855, 1684993, 5179890, 4295296, 1840251, 10684958, 4138182, 67611]
    count_id_com = 0
    for id_com in id_company:
        company_data = get_employers_info(id_com)
        # Наполняем таблицу employers
        save_company_to_db(company_data, 'postgres', '29051989')


if __name__ == '__main__':
    user_interaction()
