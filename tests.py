from unittest import TestCase
from table_out import bool_converter


class Test(TestCase):
    def test_bool_true(self):
        self.assertEqual(bool_converter('True'), 'Да')

    def test_bool_false(self):
        self.assertEqual(bool_converter('False'), 'Нет')

    def test_bool_yes(self):
        self.assertEqual(bool_converter('Да'), True)

    def test_bool_no(self):
        self.assertEqual(bool_converter('Нет'), False)

    def test_bool_invalid(self):
        self.assertEqual(bool_converter(0), 'Неверные входные данные')


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


def cut_params(num_vac, interval):
    """Осуществляет нахождение диапазона вывода вакансий.

    Returns:
        list: Начало, конец интервала

    >>> cut_params(857, '')
    (0, 857)
    >>> cut_params(857, '10')
    (9, 857)
    >>> cut_params(857, '10 20')
    (9, 19)
    """
    if interval == '':
        start, end = 0, num_vac
    elif interval.isnumeric():
        start, end = int(interval) - 1, num_vac
    else:
        start, end = interval.split()
        start, end = int(start) - 1, int(end) - 1
    return start, end


def check_filter_param(filter_param):
    """Осуществляет проверку корретности параметра фильтрации.

    Returns:
        str: Параметр фильтрации

    >>> check_filter_param('Компания: Аконит-Урал')
    'Компания: Аконит-Урал'
    >>> check_filter_param('Название Программист')
    Формат ввода некорректен
    >>> check_filter_param('')
    ''
    >>> check_filter_param('qwerty: Да')
    Параметр поиска некорректен
    >>> check_filter_param('23')
    Формат ввода некорректен
    """
    if ': ' not in filter_param and filter_param != '':
        return print('Формат ввода некорректен')
    elif filter_param.split(': ')[0] not in rus_names.values() and filter_param != '':
        return print('Параметр поиска некорректен')
    return filter_param


def check_sort_param(sort_param):
    """Осуществляет проверку корретности параметра сортировки.

    Returns:
        str: Параметр сортировки

    >>> check_sort_param('')
    ''
    >>> check_sort_param('Оклад')
    'Оклад'
    >>> check_sort_param('Профессия')
    Параметр сортировки некорректен
    >>> check_sort_param(21)
    Параметр сортировки некорректен
    """
    if sort_param not in rus_names.values() and sort_param != '':
        return print('Параметр сортировки некорректен')
    return sort_param


def check_is_reverse_sort(is_reverse_sort):
    """Осуществляет проверку корретности порядока сортировки.

    Returns:
        bool: Порядок сортировки

    >>> check_is_reverse_sort('')
    False
    >>> check_is_reverse_sort('Да')
    True
    >>> check_is_reverse_sort('Нет')
    False
    >>> check_is_reverse_sort('Неверные входные данные')
    Порядок сортировки задан некорректно
    >>> check_is_reverse_sort(0)
    Порядок сортировки задан некорректно
    """
    if is_reverse_sort == '':
        is_reverse_sort = False
    else:
        is_reverse_sort = bool_converter(is_reverse_sort)
    if is_reverse_sort == 'Неверные входные данные':
        return print('Порядок сортировки задан некорректно')
    return is_reverse_sort
