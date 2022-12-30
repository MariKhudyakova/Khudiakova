import math
import pandas as pd
from sqlalchemy import create_engine
import sqlite3


def get_salary(row):
    salary_from = row.salary_from
    salary_to = row.salary_to
    salary_currency = row.salary_currency
    salary = row.salary
    if type(salary_currency) is str:
        if not math.isnan(salary_from) and not math.isnan(salary_to):
            salary = (salary_from + salary_to) / 2
        elif not math.isnan(salary_from):
            salary = salary_from
        elif not math.isnan(salary_to):
            salary = salary_to
        if salary_currency != 'RUR' and salary_currency in ["BYR", "USD", "EUR", "KZT", "UAH"]:
            date = f'{row.published_at[5:7]}/{row.published_at[:4]}'
            ratio_cur = cur.execute(f"""select {salary_currency} from currency_date where date='{date}'""").fetchone()[0]
            salary = salary * ratio_cur if ratio_cur is not None else float('NaN')
        elif salary_currency != 'RUR':
            salary = float('NaN')
    return salary


conn = sqlite3.connect('currency_date.db')
cur = conn.cursor()
engine = create_engine('sqlite:///C:\\Users\\Home\\PycharmProjects\\Khudiakova\\currency_date.db')
# pd.set_option('expand_frame_repr', False)
file = 'vacancies_dif_currencies.csv'
df = pd.read_csv(file)
df.insert(1, 'salary', float('NaN'))
df['salary'] = df.apply(lambda row: get_salary(row), axis=1)
df.pop('salary_from')
df.pop('salary_to')
df.pop('salary_currency')
df['published_at'] = df['published_at'].apply(lambda s: s[:7])
connection = sqlite3.connect('vacancies_with_one_currency.db')
cursor = connection.cursor()
df.to_sql(name='vacancies_with_one_currency', con=connection, if_exists='replace', index=False)
connection.commit()
