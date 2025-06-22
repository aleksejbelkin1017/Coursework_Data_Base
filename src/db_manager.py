import psycopg2
from psycopg2 import OperationalError
from typing import List, Dict, Optional


class DBManager:
    """
    Класс для взаимодействия с базой данных PostgreSQL.

    Атрибуты:
        db_name (str): название базы данных
        user (str): имя пользователя для подключения
        password (str): пароль пользователя
        host (str): хост базы данных (по умолчанию '127.0.0.1')
        port (str): порт подключения (по умолчанию '5432')
        connection (Optional[connection]): объект подключения к БД
        cursor (Optional[cursor]): объект курсора
    """

    def __init__(self, db_name: str, user: str, password: str, host: str = "127.0.0.1", port: str = "5432"):
        """
        Инициализация объекта DBManager.

        Параметры:
            db_name (str): название базы данных
            user (str): имя пользователя для подключения
            password (str): пароль пользователя
            host (str, optional): хост базы данных. По умолчанию '127.0.0.1'
            port (str, optional): порт подключения. По умолчанию '5432'
        """
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        """
        Метод для подключения к базе данных.

        Подключается к PostgreSQL базе данных с использованием
        заданных параметров. Создает соединение и курсор.

        Вызывает исключение OperationalError в случае неудачи.
        """
        try:
            # Используем именованные параметры
            self.connection = psycopg2.connect(
                database=self.db_name, user=self.user, password=self.password, host=self.host, port=self.port
            )
            self.cursor = self.connection.cursor()  # type: ignore[attr-defined]
            # print("Подключение установлено успешно")
        except OperationalError as e:
            print(f"Ошибка подключения: {e}")
            raise

    def close(self) -> None:
        """
        Метод для отключения от базы данных.

        Закрывает соединение с базой данных и обнуляет курсор.
        """
        if self.connection:
            self.connection.close()
            self.cursor = None

    def get_companies_and_vacancies_count(self) -> List[Dict[str, str]]:
        """
        Метод для получения списка всех компаний и количества вакансий у каждой компании.

        Возвращает:
        Список словарей, где каждый словарь содержит:
        - employer_name (str): название компании
        - employer_open_vacancy (str): количество открытых вакансий

        Поднимает:
        Exception: если нет активного подключения к базе данных
        """
        try:
            # Проверяем наличие подключения
            if not self.connection:
                raise Exception("Нет активного подключения к базе данных")

            # Формируем SQL-запрос
            query = "SELECT employer_name, employer_open_vacancy FROM employers;"

            # Выполняем запрос
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            # Форматируем результат
            companies_data = [{"employer_name": row[0], "employer_open_vacancy": row[1]} for row in results]

            return companies_data
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            raise

    def get_all_vacancies(self) -> List[Dict[str, Optional[str]]]:
        """
        Метод для получения списка всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.

        Возвращает:
        Список словарей, где каждый словарь содержит:
        - company_name (str): название компании
        - vacancy_name (str): название вакансии
        - salary_min (Optional[str]): минимальная зарплата или 'Не указано'
        - salary_max (Optional[str]): максимальная зарплата или 'Не указано'
        - vacancy_url (str): ссылка на вакансию

        Поднимает:
        Exception: при ошибке выполнения SQL-запроса
        """
        try:
            query = """
            SELECT
            employers.employer_name,
            vacancies.vacancy_name,
            vacancies.salary_min,
            vacancies.salary_max,
            vacancies.vacancy_url
            FROM
            vacancies
            JOIN
            employers ON vacancies.employer_id = employers.employer_id;
            """

            self.cursor.execute(query)  # type: ignore[attr-defined]
            results = self.cursor.fetchall()  # type: ignore[attr-defined]

            def format_salary(value: Optional[int]) -> str:
                # Явная проверка на None и 0
                return "Не указано" if value is None or value == 0 else str(value)

            vacancies_data = [
                {
                    "company_name": row[0],
                    "vacancy_name": row[1],
                    "salary_min": format_salary(row[2]),
                    "salary_max": format_salary(row[3]),
                    "vacancy_url": row[4],
                }
                for row in results
            ]

            return vacancies_data
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            raise

    def get_avg_salary(self) -> Dict[str, Optional[int]]:
        """
        Метод для получения средней зарплаты по вакансиям.

        Возвращает:
        Словарь со следующими ключами:
        - avg_min (Optional[int]): средняя минимальная зарплата
        - avg_max (Optional[int]): средняя максимальная зарплата
        - avg_salary (Optional[int]): средняя зарплата

        Поднимает:
        Exception: если нет активного подключения к базе данных
        """
        try:
            # Проверяем наличие подключения
            if not self.connection:
                raise Exception("Нет активного подключения к базе данных")

            # Формируем SQL-запрос
            query = """
            SELECT
                AVG(salary_min) as avg_min,
                AVG(salary_max) as avg_max,
                (AVG(salary_min) + AVG(salary_max)) / 2 as avg_salary
            FROM vacancies
            WHERE salary_min IS NOT NULL
            AND salary_max IS NOT NULL;
            """

            # Выполняем запрос
            self.cursor.execute(query)
            result = self.cursor.fetchone()

            if result is None:
                return "Нет данных о зарплатах"

            # Возвращаем результат в виде словаря
            return {"avg_min": round(result[0]), "avg_max": round(result[1]), "avg_salary": round(result[2])}
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            raise

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Optional[int]]]:
        """
        Метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Возвращает:
        Список словарей, где каждый словарь содержит:
        - vacancy_name (str): название вакансии
        - requirement_vacancy (str): описание вакансии
        - salary_min (Optional[int]): минимальная зарплата
        - salary_max (Optional[int]): максимальная зарплата
        - avg_salary (Optional[int]): средняя зарплата по вакансии

        Поднимает:
        Exception: при ошибке выполнения SQL-запроса
        """
        try:
            # Получаем среднюю зарплату
            avg_salary = self.get_avg_salary()["avg_salary"]

            # Формируем SQL-запрос
            query = f"""
            SELECT
                vacancy_name,
                requirement_vacancy,
                salary_min,
                salary_max,
                (salary_min + salary_max) / 2 as avg_vacancy_salary
            FROM vacancies
            WHERE
                salary_min IS NOT NULL
                AND salary_max IS NOT NULL
                AND ((salary_min + salary_max) / 2) > {avg_salary}
            ORDER BY avg_vacancy_salary DESC;
            """

            # Выполняем запрос
            self.cursor.execute(query)  # type: ignore[attr-defined]
            results = self.cursor.fetchall()  # type: ignore[attr-defined]

            # Формируем список вакансий
            vacancies = []
            for row in results:
                vacancies.append(
                    {
                        "vacancy_name": row[0],
                        "requirement_vacancy": row[1],
                        "salary_min": row[2],
                        "salary_max": row[3],
                        "avg_salary": row[4],
                    }
                )

            return vacancies
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            raise

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Optional[int]]]:
        """
        Метод получает список всех вакансий, в названии которых содержатся переданные в метод слова.

        Параметры:
        keyword (str): искомое слово

        Возвращает:
        Список словарей, где каждый словарь содержит:
        - vacancy_id (int): ID вакансии
        - vacancy_name (str): наименование вакансии
        - requirement_vacancy (str): описание вакансии
        - salary_min (Optional[int]): минимальная зарплата
        - salary_max (Optional[int]): максимальная зарплата

        Поднимает:
        Exception: при ошибке выполнения SQL-запроса
        """
        try:
            # Формируем SQL-запрос с параметризованным значением
            query = """
            SELECT
                vacancy_id,
                vacancy_name,
                requirement_vacancy,
                salary_min,
                salary_max
            FROM vacancies
            WHERE LOWER(vacancy_name) LIKE %s
            ORDER BY vacancy_name;
            """

            # Подготавливаем параметр для поиска
            search_term = f"%{keyword.lower()}%"

            # Выполняем запрос с параметром
            self.cursor.execute(query, (search_term,))  # type: ignore[attr-defined]
            results = self.cursor.fetchall()  # type: ignore[attr-defined]

            # Формируем список вакансий
            vacancies = []
            for row in results:
                vacancies.append(
                    {
                        "vacancy_id": row[0],
                        "vacancy_name": row[1],
                        "requirement_vacancy": row[2],
                        "salary_min": row[3],
                        "salary_max": row[4],
                    }
                )

            return vacancies
        except Exception as e:
            print(f"Ошибка при поиске вакансий: {e}")
            raise
