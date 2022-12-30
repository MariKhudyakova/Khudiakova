import pandas as pd
import os
import sys
from numpy import mean
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from jinja2 import Environment, FileSystemLoader
import pdfkit


class UserInput:
    """Класс для пользовательского ввода.

    Attributes:
        file_name (str): Название файла
        profession_name (str): Название професии
        area (str): Название региона
    """
    def __init__(self):
        """Инициализирует объекты UserInput, выполняет проверку на корректность введенные данные.
        """
        self.file_name = input('Введите название файла: ')
        self.profession_name = input('Введите название профессии: ')
        self.area = input("Введите название региона: ")

        self.file_name = self.check_file_name(self.file_name)
        self.profession_name = self.check_profession_name_area(self.profession_name)
        self.area = self.check_profession_name_area(self.area)

    @staticmethod
    def check_file_name(file_name):
        """Осуществляет проверку корретности названия файла.

        Returns:
            str: Название файла
        """
        if file_name == '' or '.' not in file_name:
            print('Некорректное название файла')
            sys.exit()
        return file_name

    @staticmethod
    def check_profession_name_area(name):
        """Осуществляет проверку корретности названия профессии/региона.

        Returns:
            str: Название профессии/региона
        """
        if name == '':
            print('Некорректное название профессии/региона')
            sys.exit()
        return name


class GetCsvParts:
    def __init__(self, file_name):
        self.df = pd.read_csv(file_name)
        self.df['years'] = self.df['published_at'].apply(lambda s: s[:4])
        self.years = self.df['years'].unique()

        for year in self.years:
            data = self.df[self.df['years'] == year]
            data.iloc[:, :6].to_csv(rf'csv_files\part_{year}.csv', index=False)


class Salary:
    def __init__(self, df):
        self.df = df
        self.df_date = pd.read_csv("currency_date.csv")
        self.df["salary"] = df.apply(lambda row: self.get_salary(row["salary_from"], row["salary_to"], row["salary_currency"], row["published_at"][:7].split("-")), axis=1)

    def get_salary(self, salary_from, salary_to, salary_currency, date):
        date = date[1] + "/" + date[0]

        salary_currency_coef = 0
        if salary_currency == "RUR":
            salary_currency_coef = 1
        elif salary_currency != "RUR" and (salary_currency == salary_currency) and salary_currency in ["BYN", "BYR", "USD", "EUR", "KZT", "UAH"]:
            salary_currency.replace("BYN", "BYR")
            df_date_row = self.df_date.loc[self.df_date["date"] == date]
            salary_currency_coef = df_date_row[salary_currency].values[0]

        if not (math.isnan(salary_from)) and math.isnan(salary_to):
            return salary_from * salary_currency_coef
        elif math.isnan(salary_from) and not (math.isnan(salary_to)):
            return salary_to * salary_currency_coef
        elif not (math.isnan(salary_from)) and not (math.isnan(salary_to)):
            return mean([salary_from, salary_to]) * salary_currency_coef


class Report:
    def __init__(self, prof, area, dicts_by_area, dicts_by_year, others):
        self.generate_image(prof, area, dicts_by_area, dicts_by_year, others)
        self.generate_pdf(prof, area, dicts_by_area, dicts_by_year)

    @staticmethod
    def generate_image(prof, area, dicts_by_area, dicts_by_year, others):
        y1_cities = np.arange(len(dicts_by_area[0].keys()))
        y1_cities_names = {}
        for key, value in dicts_by_area[0].items():
            if "-" in key or " " in key:
                key = key.replace("-", "-\n")
                key = key.replace(" ", "\n")
            y1_cities_names[key] = value

        x_nums = np.arange(len(dicts_by_year[0].keys()))
        width = 0.4
        x_list1 = x_nums
        fig = plt.figure()

        ax1 = fig.add_subplot(221)
        ax1.set_title("Уровень зарплат по годам")
        ax1.bar(x_list1, dicts_by_year[0].values(), width, label=f"з/п {prof} ({area})")
        ax1.set_xticks(x_nums, dicts_by_year[0].keys(), rotation="vertical")
        ax1.tick_params(axis="both", labelsize=8)
        ax1.legend(fontsize=8)
        ax1.grid(True, axis="y")

        ax2 = fig.add_subplot(222)
        ax2.set_title("Количество вакансий по годам")
        ax2.bar(x_list1, dicts_by_year[1].values(), width,
               label=f"Количество вакансий \n{prof} ({area})")
        ax2.set_xticks(x_nums, dicts_by_year[1].keys(), rotation="vertical")
        ax2.tick_params(axis="both", labelsize=8)
        ax2.legend(fontsize=8)
        ax2.grid(True, axis="y")

        ax3 = fig.add_subplot(223)
        ax3.set_title("Уровень зарплат по городам")
        width = 0.8
        ax3.barh(y1_cities, dicts_by_area[0].values(), width, align="center")
        ax3.set_yticks(y1_cities, labels=y1_cities_names.keys(), horizontalalignment="right", verticalalignment="center")
        ax3.tick_params(axis="x", labelsize=8)
        ax3.tick_params(axis="y", labelsize=6)
        ax3.xaxis.set_major_locator(ticker.MultipleLocator(100000))
        ax3.invert_yaxis()
        ax3.grid(True, axis="x")

        ax4 = fig.add_subplot(224)
        ax4.set_title("Доля вакансий по городам")
        dicts_by_area[1]["Другие"] = others
        ax4.pie(dicts_by_area[1].values(), labels=dicts_by_area[1].keys(), textprops={'size': 6},
               colors=["#ff8006", "#28a128", "#1978b5", "#0fbfd0", "#bdbe1c", "#808080", "#e478c3", "#8d554a", "#9567be", "#d72223", "#1978b5", "#ff8006"])
        ax4.axis('equal')

        plt.tight_layout()
        plt.savefig("graph.png")

    @staticmethod
    def generate_pdf(prof, area, dicts_by_area, dicts_by_year):
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("pdf_template.html")

        pdf_template = template.render(
            {'prof': prof, 'area': area, 'by_area': dicts_by_area, 'by_year': dicts_by_year,
             'keys_0_area': list(dicts_by_area[0].keys()), 'values_0_area': list(dicts_by_area[0].values()),
             'keys_1_area': list(dicts_by_area[1].keys()), 'values_1_area': list(dicts_by_area[1].values())})

        options = {'enable-local-file-access': None}
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options=options)
        os.remove('graph.png')


def sort_area_dict(dictionary):
    sorted_tuples = sorted(dictionary.items(), key=lambda item: item[1], reverse=True)[:10]
    sorted_dict = {k: v for k, v in sorted_tuples}
    return sorted_dict


def output(df, years, vacancy, area):
    salary = Salary(df)
    df['salary'] = salary.df['salary']
    df['published_at'] = df['published_at'].apply(lambda x: int(x[:4]))

    total = len(df)
    df['count'] = df.groupby('area_name')['area_name'].transform('count')
    df_norm = df[df['count'] > 0.01 * total]
    cities = df_norm["area_name"].unique()
    others = len(df[df['count'] < 0.01 * total]) / total

    salary_lvl_by_city, vacancy_rate_by_city, salary_area_lvl_by_year, salary_area_count = {}, {}, {}, {}

    for city in cities:
        df_city = df_norm[df_norm['area_name'] == city]
        salary_lvl_by_city[city] = int(mean(df_city['salary']))
        vacancy_rate_by_city[city] = round(len(df_city) / len(df), 4)

    df_vacancy = df[df["name"].str.contains(vacancy)]
    for year in years:
        df_salary_vacancy = df_vacancy[(df_vacancy['years'] == year) & (df_vacancy['area_name'] == area)]
        if not df_salary_vacancy.empty:
            salary_area_lvl_by_year[year] = int(df_salary_vacancy['salary'].mean()) if not math.isnan(df_salary_vacancy['salary'].mean()) else 'NaN'
            salary_area_count[year] = len(df_salary_vacancy)

    print("Уровень зарплат по городам (в порядке убывания):", sort_area_dict(salary_lvl_by_city))
    print("Доля вакансий по городам (в порядке убывания):", sort_area_dict(vacancy_rate_by_city))
    print("Динамика уровня зарплат по годам для выбранной профессии и региона:", salary_area_lvl_by_year)
    print("Динамика количества вакансий по годам для выбранной профессии и региона:", salary_area_count)

    return [sort_area_dict(salary_lvl_by_city), sort_area_dict(vacancy_rate_by_city), salary_area_lvl_by_year, salary_area_count, others]


pd.set_option("expand_frame_repr", False)

user_input = UserInput()
csv_files = GetCsvParts(user_input.file_name)
output_data = output(csv_files.df, csv_files.years, user_input.profession_name, user_input.area)
dicts_list_by_area = [output_data[0], output_data[1]]
dicts_list_by_year = [output_data[2], output_data[3]]
report = Report(user_input.profession_name, user_input.area, dicts_list_by_area, dicts_list_by_year, output_data[4])
