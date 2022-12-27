import pandas as pd
from pandas import json_normalize
import requests

pd.set_option("expand_frame_repr", False)

df_day_salary = pd.DataFrame()
times = ['00:00:01', '06:00:00', '12:00:00', '18:00:00', '23:59:59']
for i in range(1, len(times)):
    for j in range(20):
        page = requests.get(f'https://api.hh.ru/vacancies?specialization=1&per_page=100&page={j}&date_from=2022-12-26T{times[i - 1]}&date_to=2022-12-26T{times[i]}').json()
        vacancies = page["items"]
        if len(vacancies) == 0:
            break
        df = json_normalize(vacancies)
        df1 = df[["name", 'salary.from', 'salary.to', 'salary.currency', 'area.name', 'published_at']]
        df1.columns = df1.columns.str.replace('.', '_', regex=False)
        df_day_salary = pd.concat([df_day_salary, df1], ignore_index=True, axis=0)

df_day_salary.to_csv('vacancies_by_day.csv', index=False)
