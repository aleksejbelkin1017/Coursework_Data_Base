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
            print(f"База данных '{db_name}' успешно создана.")
        else:
            print(f"База данных '{db_name}' уже существует.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при работе с базой данных: {error}")
    finally:
        # Закрытие соединения
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с PostgreSQL закрыто.")

# Использование функции
create_database_if_not_exists('company_vacations_database', 'postgres', '29051989')