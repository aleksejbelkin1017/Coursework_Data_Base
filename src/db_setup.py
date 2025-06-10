import psycopg2


def create_database_if_not_exists(db_name, user, password, host='127.0.0.1', port='5432'):
    """
    Функция для создания базы данных в случае её отсутствия
    :param db_name: имя создаваемой базы данных
    :param user: имя пользователя базы данных
    :param password: пароль от базы данных
    :param host: хост, по умолчанию 127.0.0.1
    :param port: номер порта, по умолчанию 5432
    :return: создает базу данных с заданным наименованием либо возвращает сообщение о существовании такой базы данных
    """
    try:
        # Подключение к серверу базы данных
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database="postgres"
        )
        connection.autocommit = True

        # Создание курсора
        cursor = connection.cursor()

        # Проверка на существование базы данных
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cursor.fetchone()

        if not exists:
            # Выполнение команды создания базы данных, если она не существует
            cursor.execute(f"CREATE DATABASE {db_name};")
            #print(f"База данных '{db_name}' успешно создана.")
        else:
            print(f"База данных '{db_name}' создана ранее.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при работе с базой данных: {error}")
    finally:
        # Закрытие соединения
        if connection:
            cursor.close()
            connection.close()
            # print("Соединение с PostgreSQL закрыто.")

# Использование функции
# create_database_if_not_exists('company_vacations_database', 'postgres', '29051989')


# Функция для создания таблицы с проверкой
def create_table_if_not_exists(dbname, user, password, host, table_name, columns_sql):
    try:
        # Подключаемся к базе данных
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )

        # Создаем курсор для выполнения SQL-запросов
        cursor = connection.cursor()

        # Формируем SQL-запрос для создания таблицы, если она не существует
        create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});'

        # Выполняем запрос
        cursor.execute(create_table_query)

        # Сохраняем изменения в базе данных
        connection.commit()

        print(f"Таблица '{table_name}' успешно создана.")
    except Exception as error:
        print(f"Ошибка при создании таблицы: {error}")
    finally:
        # Закрываем курсор и соединение
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def save_company_to_db(company_data, user, password):
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            dbname="employers_vacancies_database",
            user=user,
            password=password,
            host="localhost"
        )

        # Создаем курсор
        cur = conn.cursor()

        # Проверяем, существует ли уже компания в базе
        cur.execute("SELECT employer_id FROM employers WHERE employer_id = %s", (company_data['id'],))
        existing_company = cur.fetchone()

        if existing_company:
            # Если компания уже есть, обновляем данные
            cur.execute("""
                UPDATE employers 
                SET employer_name = %s, 
                    employer_url = %s, 
                    employer_open_vacancy = %s 
                WHERE employer_id = %s
            """, (
            company_data['name'], company_data['alternate_url'], company_data['open_vacancies'], company_data['id']))
        else:
            # Если компании нет, добавляем новую запись
            cur.execute("""
                INSERT INTO employers (employer_id, employer_name, employer_url, employer_open_vacancy) 
                VALUES (%s, %s, %s, %s)
            """, (
            company_data['id'], company_data['name'], company_data['alternate_url'], company_data['open_vacancies']))

        # Применяем изменения
        conn.commit()

        # Закрываем соединение
        cur.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
        return False


def save_vacancies_to_db(vacancies_data, user, password):
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            dbname="employers_vacancies_database",
            user=user,
            password=password,
            host="localhost"
        )

        cur = conn.cursor()

        # Проходим по всем вакансиям
        for vacancy in vacancies_data.get('items', []):
            # Собираем данные для вставки
            salary = vacancy.get('salary')
            data = {
                'vacancy_id': vacancy.get('id'),
                'vacancy_name': vacancy.get('name', 'Не указано'),
                'employer_name': vacancy.get('employer', {}).get('name', 'Не указано'),
                'employer_id': vacancy.get('employer', {}).get('id', 'Не указано'),
                'salary_min': salary.get('from', 0) if salary else 0,
                'salary_max': salary.get('to', 0) if salary else 0,
                'vacancy_url': vacancy.get('alternate_url', 'Не указано')
            }
            # print(f"Сохраняем вакансию: {data}")
            # Проверяем существование вакансии
            cur.execute("SELECT vacancy_id FROM vacancies WHERE vacancy_id = %s", (data['vacancy_id'],))
            existing_vacancy = cur.fetchone()

            if existing_vacancy:
                # Если вакансия уже есть, обновляем данные
                cur.execute("""
                UPDATE vacancies 
                SET vacancy_name = %s, 
                    employer_name = %s, 
                    employer_id = %s, 
                    salary_min = %s, 
                    salary_max = %s, 
                    vacancy_url = %s 
                WHERE vacancy_id = %s
                """, (
                    data['vacancy_name'],
                    data['employer_name'],
                    data['employer_id'],
                    data['salary_min'],
                    data['salary_max'],
                    data['vacancy_url'],
                    data['vacancy_id']
                ))
            else:
                # Если вакансии нет, добавляем новую запись
                cur.execute("""
                INSERT INTO vacancies (
                    vacancy_id, 
                    vacancy_name, 
                    employer_name, 
                    employer_id, 
                    salary_min, 
                    salary_max, 
                    vacancy_url
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data['vacancy_id'],
                    data['vacancy_name'],
                    data['employer_name'],
                    data['employer_id'],
                    data['salary_min'],
                    data['salary_max'],
                    data['vacancy_url']
                ))

        # Применяем изменения
        conn.commit()
        cur.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Ошибка при сохранении данных для вакансии: {vacancy.get('id', 'Не указано')}, ошибка: {e}")
        return False