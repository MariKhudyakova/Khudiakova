import pandas as pd
import math
from numpy import mean


pd.set_option("expand_frame_repr", False)
df = pd.read_csv("vacancies_dif_currencies.csv")
df_date = pd.read_csv("currency_date.csv")
df.insert(1, "salary", "NaN")


def get_salary(salary_from, salary_to, salary_currency, date):
    date = date[1] + "/" + date[0]

    salary_currency_coef = 0
    if salary_currency == "RUR":
        salary_currency_coef = 1
    elif salary_currency != "RUR" and (salary_currency == salary_currency) and salary_currency in ["BYN", "BYR", "USD", "EUR", "KZT", "UAH"]:
        salary_currency.replace("BYN", "BYR")
        df_date_row = df_date.loc[df_date["date"] == date]
        salary_currency_coef = df_date_row[salary_currency].values[0]

    if not (math.isnan(salary_from)) and math.isnan(salary_to):
        return salary_from * salary_currency_coef
    elif math.isnan(salary_from) and not (math.isnan(salary_to)):
        return salary_to * salary_currency_coef
    elif not (math.isnan(salary_from)) and not (math.isnan(salary_to)):
        return mean([salary_from, salary_to]) * salary_currency_coef


df["salary"] = df.apply(lambda row: get_salary(row["salary_from"], row["salary_to"], row["salary_currency"], row["published_at"][:7].split("-")), axis=1)
df.pop('salary_from')
df.pop('salary_to')
df.pop('salary_currency')
# df[:100].to_csv("vacancies_with_one_currency.csv", index=False)
