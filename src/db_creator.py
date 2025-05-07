import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional
from utils import config


class DBCreator:
    """Класс для создания базы данных и таблиц"""

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.params = config()

    def create_database(self) -> None:
        """Создание базы данных"""
        conn = psycopg2.connect(dbname='postgres', **self.params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        try:
            # Завершаем все соединения с базой
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{self.db_name}'
                AND pid <> pg_backend_pid();
            """)

            # Проверяем существование БД
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{self.db_name}'")
            exists = cursor.fetchone()

            if exists:
                cursor.execute(f"DROP DATABASE {self.db_name}")

            cursor.execute(f"CREATE DATABASE {self.db_name}")
        except psycopg2.Error as e:
            print(f"Ошибка при создании базы данных: {e}")
        finally:
            cursor.close()
            conn.close()

    def create_tables(self) -> None:
        """Создание таблиц в базе данных"""
        commands = (
            """
            DROP TABLE IF EXISTS vacancies;
            DROP TABLE IF EXISTS employers;
            """,
            """
            CREATE TABLE employers (
                employer_id VARCHAR PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255),
                description TEXT
            )
            """,
            """
            CREATE TABLE vacancies (
                vacancy_id VARCHAR PRIMARY KEY,
                employer_id VARCHAR REFERENCES employers(employer_id),
                title VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                url VARCHAR(255),
                requirements TEXT
            )
            """
        )

        conn = None
        try:
            params = self.params.copy()
            params.update({'dbname': self.db_name})
            conn = psycopg2.connect(**params)
            cursor = conn.cursor()

            for command in commands:
                cursor.execute(command)

            conn.commit()
            cursor.close()
        except psycopg2.Error as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            if conn is not None:
                conn.close()