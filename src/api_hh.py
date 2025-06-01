import requests
import time


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


# Используем найденный ID работодателя
vacancies = get_employer_vacancies(67611)
count_vac = 0

# Выводим информацию о вакансиях
for vacancy in vacancies:
    print(f"ID вакансии: {vacancy['id']}")
    print(f"Название: {vacancy['name']}")
    print(f"Зарплата: {vacancy.get('salary', 'Не указана')}")
    print(f"Город: {vacancy['area']['name']}")
    print(f"Ссылка: {vacancy['alternate_url']}")
    print('-' * 50)
    count_vac += 1

print(count_vac)
