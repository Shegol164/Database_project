import requests
import time
from typing import Dict, List


class HeadHunterAPI:
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.base_url = "https://api.hh.ru/"

    def get_employers(self, employer_ids: List[str]) -> List[Dict]:
        """Получение данных о работодателях по их ID"""
        employers = []
        for employer_id in employer_ids:
            url = f"{self.base_url}employers/{employer_id}"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                employer_data = response.json()
                employers.append({
                    'employer_id': employer_data['id'],  # Изменили 'id' на 'employer_id'
                    'name': employer_data['name'],
                    'url': employer_data['site_url'] if employer_data.get('site_url') else None,
                    'description': employer_data['description'] if employer_data.get('description') else None
                })

                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе данных работодателя {employer_id}: {e}")
                continue

        return employers

    def get_vacancies(self, employer_id: str) -> List[Dict]:
        """Получение вакансий работодателя по его ID"""
        url = f"{self.base_url}vacancies"
        params = {
            'employer_id': employer_id,
            'per_page': 100,
            'page': 0
        }
        vacancies = []

        try:
            while True:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()
                vacancies.extend(data['items'])

                if data['pages'] <= params['page'] + 1:
                    break
                params['page'] += 1
                time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении вакансий: {e}")

        processed_vacancies = []
        for vacancy in vacancies:
            salary = vacancy.get('salary')
            processed_vacancies.append({
                'vacancy_id': vacancy['id'],  # Изменили 'id' на 'vacancy_id'
                'employer_id': employer_id,
                'title': vacancy['name'],
                'salary_from': salary['from'] if salary and salary.get('from') else None,
                'salary_to': salary['to'] if salary and salary.get('to') else None,
                'currency': salary['currency'] if salary and salary.get('currency') else None,
                'url': vacancy['alternate_url'],
                'requirements': vacancy['snippet']['requirement'] if vacancy['snippet'].get('requirement') else None
            })

        return processed_vacancies