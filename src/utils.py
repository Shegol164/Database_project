import os
from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    # Получаем абсолютный путь к файлу
    filepath = os.path.join(os.path.dirname(__file__), '..', 'config', filename)

    parser = ConfigParser()
    parser.read(filepath)

    if parser.has_section(section):
        return dict(parser.items(section))
    else:
        raise Exception(f'Section {section} not found in the {filepath} file')
