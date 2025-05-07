from api import HeadHunterAPI  # Убрали src.
from db_creator import DBCreator
from db_manager import DBManager
from typing import List
import time  # Добавим для задержки
import sys  # Для обработки ошибок


def main():
    try:
        # ID компаний для сбора данных
        COMPANY_IDS = [
            '1740', '3529', '78638', '2748', '3776',
            '41862', '87021', '2180', '4934', '1122462'
        ]

        DB_NAME = 'hh_vacancies'

        print("Создание базы данных и таблиц...")
        db_creator = DBCreator(DB_NAME)
        db_creator.create_database()
        db_creator.create_tables()

        print("Получение данных с hh.ru...")
        hh_api = HeadHunterAPI()
        employers = hh_api.get_employers(COMPANY_IDS)

        print("Сохранение данных о компаниях...")
        db_manager = DBManager(DB_NAME)
        db_manager.insert_data('employers', employers)

        print("Получение и сохранение вакансий...")
        for employer_id in COMPANY_IDS:
            print(f"Обработка вакансий для компании ID: {employer_id}")
            vacancies = hh_api.get_vacancies(employer_id)
            if vacancies:
                db_manager.insert_data('vacancies', vacancies)
            time.sleep(1)  # Задержка между запросами

        user_interface(db_manager)

    except KeyboardInterrupt:
        print("\nПрограмма была остановлена пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        sys.exit(1)

def user_interface(db_manager):
    """Интерфейс взаимодействия с пользователем"""
    while True:
        print("\nВыберите действие:")
        print("1. Список компаний и количество вакансий")
        print("2. Список всех вакансий")
        print("3. Средняя зарплата по вакансиям")
        print("4. Вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("> ")

        if choice == '1':
            companies = db_manager.get_companies_and_vacancies_count()
            for company in companies:
                print(f"{company['name']}: {company['vacancies_count']} вакансий")

        elif choice == '2':
            vacancies = db_manager.get_all_vacancies()
            for vacancy in vacancies:
                salary = format_salary(vacancy)
                print(f"{vacancy['company']}: {vacancy['title']} - {salary}")
                print(f"Ссылка: {vacancy['url']}\n")


        elif choice == '3':

            avg_salary = db_manager.get_avg_salary()

            if avg_salary and avg_salary[0]['avg_salary']:

                print(f"Средняя зарплата: {int(avg_salary[0]['avg_salary'])} руб.")

            else:

                print("Недостаточно данных для расчета средней зарплаты")

        elif choice == '4':
            vacancies = db_manager.get_vacancies_with_higher_salary()
            if vacancies:
                print("Вакансии с зарплатой выше средней:")
                for vacancy in vacancies:
                    salary = f"{(vacancy['salary_from'] + vacancy['salary_to']) / 2} {vacancy['currency']}"
                    print(f"{vacancy['company']}: {vacancy['title']} - {salary}")
                    print(f"Ссылка: {vacancy['url']}\n")
            else:
                print("Нет вакансий с зарплатой выше средней")

        elif choice == '5':
            keyword = input("Введите ключевое слово для поиска: ")
            vacancies = db_manager.get_vacancies_with_keyword(keyword)
            if vacancies:
                print(f"Найдено {len(vacancies)} вакансий по запросу '{keyword}':")
                for vacancy in vacancies:
                    print(f"{vacancy['company']}: {vacancy['title']}")
                    print(f"Ссылка: {vacancy['url']}\n")
            else:
                print(f"Вакансий по запросу '{keyword}' не найдено")

        elif choice == '0':
            break

        else:
            print("Неверный ввод. Попробуйте еще раз.")

def format_salary(vacancy):
    """Форматирование отображения зарплаты"""
    if vacancy['salary_from'] and vacancy['salary_to']:
        return f"от {vacancy['salary_from']} до {vacancy['salary_to']} {vacancy['currency']}"
    elif vacancy['salary_from']:
        return f"от {vacancy['salary_from']} {vacancy['currency']}"
    elif vacancy['salary_to']:
        return f"до {vacancy['salary_to']} {vacancy['currency']}"
    return "не указана"


if __name__ == "__main__":
    main()