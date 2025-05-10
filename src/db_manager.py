import psycopg2
from typing import List, Dict, Optional
from utils import config


class DBManager:
    """Класс для управления базой данных вакансий"""

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.params = config()
        self.params.update({'dbname': self.db_name})

    def execute_query(self, query: str, fetch: bool = True) -> Optional[List[Dict]]:
        """Выполнение SQL-запроса"""
        conn = psycopg2.connect(**self.params)
        cursor = conn.cursor()
        result = None

        try:
            cursor.execute(query)
            if fetch:
                columns = [desc[0] for desc in cursor.description]
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.commit()
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
        finally:
            cursor.close()
            conn.close()

        return result

    def get_companies_and_vacancies_count(self) -> List[Dict]:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        query = """
            SELECT e.name, COUNT(v.vacancy_id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.name
            ORDER BY vacancies_count DESC
        """
        return self.execute_query(query)

    def get_all_vacancies(self) -> List[Dict]:
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию"""
        query = """
            SELECT e.name as company, v.title, 
                   v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            ORDER BY e.name, v.salary_from DESC
        """
        return self.execute_query(query)

    def get_avg_salary(self) -> List[Dict]:
        """Получает среднюю зарплату по вакансиям"""
        query = """
            SELECT AVG((salary_from + salary_to) / 2) as avg_salary
            FROM vacancies
            WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
        """
        return self.execute_query(query)

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        query = """
            SELECT e.name as company, v.title, 
                   v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (v.salary_from + v.salary_to) / 2 > (
                SELECT AVG((salary_from + salary_to) / 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
            )
            ORDER BY (v.salary_from + v.salary_to) / 2 DESC
        """
        return self.execute_query(query)

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """Получает список всех вакансий, в названии которых содержатся переданные слова"""
        query = f"""
            SELECT e.name as company, v.title, 
                   v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(v.title) LIKE LOWER('%{keyword}%')
            ORDER BY e.name, v.salary_from DESC
        """
        return self.execute_query(query)

    def insert_data(self, table: str, data: List[Dict]) -> None:
        """Вставка данных в таблицу"""
        conn = psycopg2.connect(**self.params)
        cursor = conn.cursor()

        try:
            for item in data:
                # Для совместимости со старым кодом можно добавить преобразование ключей
                if 'id' in item and table == 'employers':
                    item['employer_id'] = item.pop('id')
                elif 'id' in item and table == 'vacancies':
                    item['vacancy_id'] = item.pop('id')

                columns = item.keys()
                values = [item[column] for column in columns]

                insert_query = f"""
                    INSERT INTO {table} ({', '.join(columns)})
                    VALUES ({', '.join(['%s'] * len(values))})
                    ON CONFLICT DO NOTHING
                """
                cursor.execute(insert_query, values)

            conn.commit()
        except psycopg2.Error as e:
            print(f"Ошибка при вставке данных: {e}")
        finally:
            cursor.close()
            conn.close()
