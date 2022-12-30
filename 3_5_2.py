import math
from statistics import mean
import pandas as pd
import sqlite3


def get_salary(salary_from, salary_to, salary_currency, date):
    date = date[1] + "/" + date[0]

    salary_currency_coef = 0
    if salary_currency == "RUR":
        salary_currency_coef = 1
    elif salary_currency != "RUR" and (salary_currency == salary_currency) and salary_currency in ["BYN", "BYR", "USD", "EUR", "KZT", "UAH"]:
        salary_currency.replace("BYN", "BYR")
        cursor.execute("SELECT * FROM currency_date WHERE date == :year_month", {"year_month": date})
        salary_currency_coef = cursor.fetchall()[0][s_cur_to_digits[salary_currency]]

    if not (math.isnan(salary_from)) and math.isnan(salary_to):
        return salary_from * salary_currency_coef
    elif math.isnan(salary_from) and not (math.isnan(salary_to)):
        return salary_to * salary_currency_coef
    elif not (math.isnan(salary_from)) and not (math.isnan(salary_to)):
        return mean([salary_from, salary_to]) * salary_currency_coef


s_cur_to_digits = {"BYR": 1, "USD": 2, "EUR": 3, "KZT": 4, "UAH": 5}
df = pd.read_csv("vacancies_dif_currencies.csv")
connection = sqlite3.connect("currency_date.db")
cursor = connection.cursor()

df["published_at"] = df["published_at"].apply(lambda date: date[:7])
df.insert(1, "salary", df.apply(lambda row: get_salary(row["salary_from"], row["salary_to"], row["salary_currency"],
                                                       row["published_at"].split("-")), axis=1))
df.drop(["salary_from", "salary_to", "salary_currency"], axis=1, inplace=True)
df = df[df["salary"].notnull()]
df["salary"] = df["salary"].apply(lambda salary: int(salary))

connection_new_table = sqlite3.connect("vacancies_with_one_currency.db")
cursor_new_table = connection_new_table.cursor()
df.to_sql(name="vacancies_with_one_currency", con=connection_new_table, if_exists='replace', index=False)
cursor_new_table.execute("SELECT * FROM vacancies_with_one_currency")
connection_new_table.commit()

print("Худякова Мария Сергеевна")
