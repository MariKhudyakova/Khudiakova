import pandas as pd
import sqlite3

conn = sqlite3.connect('vacancies_with_one_currency.db')
cur = conn.cursor()
pd.set_option('expand_frame_repr', False)
vacancy_name = input('Введите название профессии: ')


def print_statistics(vacancy):
    salary_lvl_by_year = pd.read_sql("SELECT years AS date, ROUND(AVG(salary)) AS avg_salary "
                      "FROM vacancies_with_one_currency "
                      "GROUP BY years", conn)

    count_vac_by_year = pd.read_sql("SELECT years AS date, COUNT(salary) AS count_vacancy "
                      "FROM vacancies_with_one_currency "
                      "GROUP BY years", conn)

    salary_lvl_by_year_for_prof = pd.read_sql(f"""SELECT years AS date, ROUND(AVG(salary)) AS avg_salary
                        FROM vacancies_with_one_currency
                        WHERE name LIKE '%{vacancy}%'
                        GROUP BY years""", conn)

    count_vac_by_year_for_prof = pd.read_sql(f"""SELECT years as date, COUNT(salary) AS count_vacancy
                        FROM vacancies_with_one_currency
                        WHERE name LIKE '%{vacancy}%'
                        GROUP BY years""", conn)

    database_length = pd.read_sql("SELECT COUNT(*) FROM vacancies_with_one_currency", conn).to_dict()["COUNT(*)"][0]
    query_salary = pd.read_sql("SELECT area_name, ROUND(AVG(salary)) AS avg_salary, COUNT(area_name) FROM vacancies_with_one_currency "
                               "GROUP BY area_name "
                               "ORDER BY ROUND(AVG(salary)) DESC ", conn)

    query_salary = query_salary[query_salary["COUNT(area_name)"] >= 0.01 * database_length]
    query_salary = query_salary.drop(query_salary.columns[[2]], axis=1)
    query_salary.reset_index(drop=True, inplace=True)
    salary_lvl_by_city = query_salary.head(10)

    query_rate = pd.read_sql("SELECT area_name, COUNT(area_name) AS percent FROM vacancies_with_one_currency "
                             "GROUP BY area_name "
                             "ORDER BY COUNT(area_name) DESC LIMIT 10", conn)
    query_rate["percent"] = round(query_rate["percent"] / database_length, 4)
    vacancy_rate_by_city = query_rate
    return salary_lvl_by_year, count_vac_by_year, salary_lvl_by_year_for_prof, count_vac_by_year_for_prof, salary_lvl_by_city, vacancy_rate_by_city


statistics = print_statistics(vacancy_name)
print(f'Динамика уровня зарплат по годам:\n{statistics[0]}')
print(f'Динамика количества вакансий по годам:\n{statistics[1]}')
print(f'Динамика уровня зарплат по годам для выбранной профессии:\n{statistics[2]}')
print(f'Динамика количества вакансий по годам для выбранной профессии:\n{statistics[3]}')
print(f'Уровень зарплат по городам (в порядке убывания):\n{statistics[4]}')
print(f'Доля вакансий по городам (в порядке убывания):\n{statistics[5]}')
