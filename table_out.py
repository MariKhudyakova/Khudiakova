import csv
import re
import datetime
import sys
from datetime import datetime
from prettytable import PrettyTable

rus_names = {'name': 'Название',
             'description': 'Описание',
             'key_skills': 'Навыки',
             'experience_id': 'Опыт работы',
             'premium': 'Премиум-вакансия',
             'employer_name': 'Компания',
             'salary_from': 'Нижняя граница вилки оклада',
             'salary_to': 'Верхняя граница вилки оклада',
             'salary_gross': 'Оклад указан до вычета налогов',
             'salary_currency': 'Идентификатор валюты оклада',
             'area_name': 'Название региона',
             'published_at': 'Дата публикации вакансии',
             'salary': 'Оклад'}
# salary_currency
currency = {'AZN': 'Манаты',
            'BYR': 'Белорусские рубли',
            'EUR': 'Евро',
            'GEL': 'Грузинский лари',
            'KGS': 'Киргизский сом',
            'KZT': 'Тенге',
            'RUR': 'Рубли',
            'UAH': 'Гривны',
            'USD': 'Доллары',
            'UZS': 'Узбекский сум'}
# experience_id
work_experience = {'noExperience': 'Нет опыта',
                   'between1And3': 'От 1 года до 3 лет',
                   'between3And6': 'От 3 до 6 лет',
                   'moreThan6': 'Более 6 лет'}
work_experience_weight = {'noExperience': 0,
                          'between1And3': 1,
                          'between3And6': 2,
                          'moreThan6': 3}
currency_to_rub = {'AZN': 35.68,
                   'BYR': 23.91,
                   'EUR': 59.90,
                   'GEL': 21.74,
                   'KGS': 0.76,
                   'KZT': 0.13,
                   'RUR': 1,
                   'UAH': 1.64,
                   'USD': 60.66,
                   'UZS': 0.0055}


def bool_converter(data):
    """Осуществляет конвертацию логических (bool) значений.

    Returns:
        bool or str: Конвертированное значение
    """
    if data == 'True':
        return 'Да'
    elif data == 'False':
        return 'Нет'
    elif data == 'Да':
        return True
    elif data == 'Нет':
        return False
    return 'Неверные входные данные'


def get_key(val, dic):
    """Осуществляет получение в словане ключа по значению.

    Returns:
        str: Ключ полученного словаря по полученному значению
    """
    for key, value in dic.items():
        if val == value:
            return key
    return 'Ключ не существует'


class DataSet:
    """Класс для чтения csv файла.

    Attributes:
        reader (list[list[str]]): Построчно прочитанный csv файл
        columns_names (list[str]): Названия столбцов (первая строка csv файла)
        vacancies_data (list[list[str]]): Список из объеков строк (остальные строки csv файла)
    """
    def __init__(self, file_name):
        """Инициализирует объекты DataSet, записывает данные построчно в список списков.

        Args:
            file_name (str): Название csv файла
        """
        if '.' not in file_name:
            print('Ошибка в названии файла')
            sys.exit()
        self.reader = [row for row in csv.reader(open(file_name, encoding='utf_8_sig'))]
        if len(self.reader) == 0:
            print('Пустой файл')
            sys.exit()
        self.columns_names = self.reader[0]
        self.vacancies_data = [row for row in self.reader[1:] if len(row) == len(self.columns_names) and row.count('') == 0]
        if len(self.vacancies_data) == 0:
            print('Нет данных')
            sys.exit()


class Vacancy:
    """Класс для форматирования значений словаря каждой вакансии.

    Attributes:
        name (str): Название
        description (str): Описание
        key_skills (str or list): Навыки
        experience_id (str): Опыт работы
        premium (str): Премиум-вакансия
        employer_name (str): Компания
        salary_from (int or float): Нижняя граница вилки оклада
        salary_to (int or float): Верхняя граница вилки оклада
        salary_gross (str): Оклад указан до вычета налогов
        salary_currency (str): Идентификатор валюты оклада
        area_name (str): Название региона
        full_published_time (str): Дата публикации вакансии (год, месяц, день, час, минута, секунда)
        published_at (str): Дата публикации вакансии (ДД.ММ.ГГГГ)
        salary (str): Оклад
    """
    name: str
    description: str
    key_skills: str or list
    experience_id: str
    premium: str
    employer_name: str
    salary_from: int or float
    salary_to: int or float
    salary_gross: str
    salary_currency: str
    area_name: str
    full_published_time: str
    published_at: str
    salary: str

    def __init__(self, vacancy):
        """Инициализирует объекты Vacancy, форматирует значения.

        Args:
            vacancy (dict): объект одной вакансии
        """
        for key, value in vacancy.items():
            self.__setattr__(key, self.formatter(key, value))

        self.salary = f'{self.salary_from} - {self.salary_to} ({self.salary_currency}) ({self.salary_gross})'

    def formatter(self, key, value):
        """Осуществляет форматирование полученное значения.

        Returns:
            str or bool or dict: Отформатированное значение
        """
        if key == 'key_skills' and type(value) == list:
            return '\n'.join(value)
        elif key == 'premium':
            return bool_converter(value)
        elif key == 'salary_gross':
            return 'Без вычета налогов' if value == 'True' else 'С вычетом налогов'
        elif key == 'experience_id':
            return work_experience[value]
        elif key == 'salary_currency':
            return currency[value]
        elif key in ['salary_to', 'salary_from']:
            return '{:,}'.format(int(float(value))).replace(',', ' ')
        elif key == 'published_at':
            self.full_published_time = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y-%H:%M:%S')
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y')
        return value

    def check_filter_cond(self, filter_param):
        """Осуществляет проверку корретности названия файла.

        Returns:
            dict or bool: Название файла
        """
        if filter_param == '':
            return True

        filter_field, filter_value = filter_param.split(': ')
        if filter_field == 'Оклад':
            return float(self.salary_from.replace(' ', '')) <= float(filter_value) <= float(self.salary_to.replace(' ', ''))
        elif filter_field == 'Идентификатор валюты оклада':
            return self.salary_currency == filter_value
        elif filter_field == 'Навыки':
            for skill in filter_value.split(', '):
                if skill not in self.key_skills.split('\n'):
                    return False
            return True
        return self.__dict__[get_key(filter_field, rus_names)] == filter_value


class UsersInput:
    """Класс для пользовательского ввода.

    Attributes:
        file_name (str): Название файла
        filter_param (str): Параметр фильтрации
        sort_param (str): Параметр сортировки
        is_reverse_sort (str): Обратный порядок сортировки (Да / Нет)
        interval (str): Диапазон вывода
        column_names (str): Требуемые столбцы
    """
    def __init__(self):
        """Инициализирует объекты UsersInput, выполняет проверку на корректность введенные данные.
        """
        self.file_name = input('Введите название файла: ')
        self.filter_param = input('Введите параметр фильтрации: ')
        self.sort_param = input('Введите параметр сортировки: ')
        self.is_reverse_sort = input('Обратный порядок сортировки (Да / Нет): ')
        self.interval = input('Введите диапазон вывода: ')
        self.column_names = self.check_names(input('Введите требуемые столбцы: ').split(', '))

        self.filter_param = self.check_filter_param(self.filter_param)
        self.sort_param = self.check_sort_param(self.sort_param)
        self.is_reverse_sort = self.check_is_reverse_sort(self.is_reverse_sort)

    @staticmethod
    def check_sort_param(sort_param):
        """Осуществляет проверку корретности параметра сортировки.

        Returns:
            str: Параметр сортировки
        """
        if sort_param not in rus_names.values() and sort_param != '':
            print('Параметр сортировки некорректен')
            sys.exit()
        return sort_param

    @staticmethod
    def check_filter_param(filter_param):
        """Осуществляет проверку корретности параметра фильтрации.

        Returns:
            str: Параметр фильтрации
        """
        if ': ' not in filter_param and filter_param != '':
            print('Формат ввода некорректен')
            sys.exit()
        elif filter_param.split(': ')[0] not in rus_names.values() and filter_param != '':
            print('Параметр поиска некорректен')
            sys.exit()
        return filter_param

    @staticmethod
    def check_names(list_column_names):
        """Осуществляет проверку корретности требуемых столбцов.

        Returns:
            list: Названия столбцов
        """
        if '' in list_column_names:
            list_column_names = ['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии']
        list_column_names.insert(0, '№')
        return list_column_names

    @staticmethod
    def check_is_reverse_sort(is_reverse_sort):
        """Осуществляет проверку корретности порядока сортировки.

        Returns:
            bool: Порядок сортировки
        """
        if is_reverse_sort == '':
            is_reverse_sort = False
        else:
            is_reverse_sort = bool_converter(is_reverse_sort)
        if is_reverse_sort == 'Неверные входные данные':
            print('Порядок сортировки задан некорректно')
            sys.exit()
        return is_reverse_sort


class Table:
    """Класс для создания таблицы с помощью модуля PrettyTable.

    Attributes:
        table (PrettyTable): Таблица
    """
    def __init__(self):
        """Инициализирует объекты Table, задает некоторые параметры таблицы.
        """
        self.table = PrettyTable(['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии'])
        self.table.align = 'l'
        self.table.hrules = 1
        self.table.max_width = 20

    def print(self, data_vacancies, start, end, column_names):
        """Выводит вакансии в виде таблицы.
        """
        for i, vacancy in enumerate(data_vacancies):
            row = [i + 1]
            for name in self.table.field_names[1:]:
                vacancy_value = vacancy.__dict__[get_key(name, rus_names)]
                if len(vacancy_value) > 100:
                    vacancy_value = vacancy_value[:100] + '...'
                row.append(vacancy_value)
            self.table.add_row(row)

        print(self.table.get_string(start=start, end=end, fields=column_names))


def get_vacancies(data_vacancies, filter_param, sort_param, is_reverse_sort, column_names):
    """Формирует сортированный, фильтрованный список вакансий.

    Returns:
        list: Список вакансий
    """
    filtered_vacancies = []
    for data_vacancy in data_vacancies:
        parsed_data_vacancies = Vacancy(dict(zip(column_names, map(del_extra, data_vacancy))))
        if parsed_data_vacancies.check_filter_cond(filter_param):
            filtered_vacancies.append(parsed_data_vacancies)
    return vacancies_sorter(filtered_vacancies, sort_param, is_reverse_sort)


def vacancies_sorter(data_vacancies, sort_param, is_reverse_sort):
    """Получает сортированный список значений.

    Returns:
        list: Сортированный список значений
    """
    if sort_param == '':
        return data_vacancies
    data_vacancies = get_sorted_vacancies(data_vacancies, sort_param, is_reverse_sort)
    return data_vacancies


def get_sorted_vacancies(data_vacancies, sort_param, is_reverse_sort):
    """Осуществляет сортировку по параметру.

    Returns:
        list: Сортированный список значений
    """
    if sort_param in ['Название', 'Описание', 'Компания', 'Название региона']:
        data_vacancies.sort(key=lambda vacancy: vacancy.__getattribute__(get_key(sort_param, rus_names)), reverse=is_reverse_sort)
    elif sort_param == 'Дата публикации вакансии':
        data_vacancies.sort(key=lambda vacancy: vacancy.full_published_time, reverse=is_reverse_sort)
    elif sort_param == 'Навыки':
        data_vacancies.sort(key=lambda vacancy: vacancy.key_skills.count('\n'), reverse=is_reverse_sort)
    elif sort_param == 'Опыт работы':
        data_vacancies.sort(key=lambda vacancy: work_experience_weight[get_key(vacancy.experience_id, work_experience)], reverse=is_reverse_sort)
    elif sort_param == 'Оклад':
        data_vacancies.sort(key=lambda vacancy: (float(vacancy.salary_from.replace(' ', '')) + float(vacancy.salary_to.replace(' ', ''))) / 2 * currency_to_rub[get_key(vacancy.salary_currency, currency)],
                            reverse=is_reverse_sort)
    return data_vacancies


def del_extra(text):
    """Осуществляет удаление лишних данных (HTML тегов).

    Returns:
        list[str]: Список нужных данных в виде строк
    """
    text = re.sub('<.*?>', '', text)
    text = text.replace('\r\n', '\n')
    result = [' '.join(word.split()) for word in text.split('\n')]
    return result[0] if len(result) == 1 else result


def print_vacancies(data_vacancies, interval, column_names):
    """Осуществляет вывод вакансий в таблице.
    """
    if len(data_vacancies) == 0:
        print('Ничего не найдено')
        sys.exit()

    def cut_params(num_vac, interval):
        """Осуществляет нахождение интервала с какой по какую вакансию выводить.

        Returns:
            list: Начало, конец интервала
        """
        if interval == '':
            start, end = 0, num_vac
        elif interval.isnumeric():
            start, end = int(interval) - 1, num_vac
        else:
            start, end = interval.split()
            start, end = int(start) - 1, int(end) - 1
        return start, end

    start, end = cut_params(len(data_vacancies), interval)

    table = Table()
    table.print(data_vacancies, start, end, column_names)


def get_table():
    """Осуществляет создание табличных данных.
    """
    users_input = UsersInput()
    dataset = DataSet(users_input.file_name)
    (column_names, vacancies_data) = dataset.columns_names, dataset.vacancies_data
    parsed_data = get_vacancies(vacancies_data, users_input.filter_param, users_input.sort_param,
                                users_input.is_reverse_sort, column_names)
    print_vacancies(parsed_data, users_input.interval, users_input.column_names)