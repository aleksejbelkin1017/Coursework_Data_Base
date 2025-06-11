import requests  # type: ignore[import-untyped]
import time
from typing import List, Dict, Optional, Any


def get_employers_info(employer_id: int) -> Optional[Dict[str, Any]] | None:
    """
    Получает информацию о работодателе по его ID.

    Параметры:
    employer_id (int): ID работодателя

    Возвращаемое значение:
    Dict[str, Any]: словарь с информацией о работодателе или None при ошибке

    Поднимает:
    requests.RequestException: при ошибке запроса
    """
    url = f"https://api.hh.ru/employers/{employer_id}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()  # type: ignore[no-any-return]
    else:
        print(f"Ошибка при получении данных: {response.status_code}")
        return None


def get_vacancies_info(employer_id: int, page: int = 0) -> Optional[Dict[str, Any]] | None:
    """
    Получает информацию о вакансиях работодателя.

    Параметры:
    employer_id (int): ID работодателя
    page (int): номер страницы с вакансиями (по умолчанию 0)

    Возвращаемое значение:
    Dict[str, Any]: словарь с информацией о вакансиях или None при ошибке

    Поднимает:
    requests.RequestException: при ошибке запроса
    ValueError: при ошибке парсинга JSON
    """
    url = f"https://api.hh.ru/vacancies?employer_id={employer_id}&page={page}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            return response.json()  # type: ignore[no-any-return]
        except ValueError:
            print("Ошибка обработки JSON")
            return None
    else:
        print(f"Ошибка при получении данных: {response.status_code}")
        return None


def get_employer_vacancies(employer_id: int) -> List[Dict[str, Any]]:
    """
    Получает все вакансии работодателя со всех страниц.

    Параметры:
    employer_id (int): ID работодателя

    Возвращаемое значение:
    List[Dict[str, Any]]: список словарей с информацией о вакансиях

    Поднимает:
    requests.RequestException: при ошибке запроса
    """
    all_vacancies = []
    page = 0

    while True:
        params = {"employer_id": employer_id, "page": page, "per_page": 100}

        response = requests.get("https://api.hh.ru/vacancies", params=params)
        data = response.json()

        if "items" not in data:
            break

        all_vacancies.extend(data["items"])
        page += 1

        # Соблюдаем лимиты API
        time.sleep(0.5)

    return all_vacancies
