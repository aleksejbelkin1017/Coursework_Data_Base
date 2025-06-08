import requests
import time
import json


def get_employers_info(company_id):
    url = f'https://api.hh.ru/employers/{company_id}'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении данных: {response.status_code}")
        return None


# # Пример использования
# id_company = [3007832, 6780, 5179427, 10832855, 1684993, 5179890, 4295296, 1840251, 10684958, 4138182, 67611]
# count_id_com = 0
# for id_com in id_company:
#     company_data = get_employers_info(id_com)
#     if company_data:
#         print(json.dumps(company_data, ensure_ascii=False, indent=4))
#         count_id_com += 1
#
# print(count_id_com)



def get_employer_vacancies(employer_id):
    all_vacancies = []
    page = 0

    while True:
        params = {
            'employer_id': employer_id,
            'page': page,
            'per_page': 100
        }

        response = requests.get('https://api.hh.ru/vacancies', params=params)
        data = response.json()

        if 'items' not in data:
            break

        all_vacancies.extend(data['items'])
        page += 1

        # Соблюдаем лимиты API
        time.sleep(0.5)

    return all_vacancies


# # Используем найденный ID работодателя
# vacancies = get_employer_vacancies(67611)
# count_vac = 0
#
# # Выводим информацию о вакансиях
# for vacancy in vacancies:
#     print(f"ID вакансии: {vacancy['id']}")
#     print(f"Название: {vacancy['name']}")
#     print(f"Зарплата: {vacancy.get('salary', 'Не указана')}")
#     print(f"Город: {vacancy['area']['name']}")
#     print(f"Ссылка: {vacancy['alternate_url']}")
#     print('-' * 50)
#     count_vac += 1
#
# print(count_vac)
