import pandas as pd
from multiprocessing import Process, Queue


def analysis_statistics(vacancy, year, queue):
    st_df = pd.read_csv(f'csv_files\\part_{year}.csv')
    st_df.loc[:, 'salary'] = st_df.loc[:, ['salary_from', 'salary_to']].mean(axis=1)
    st_df_vacancy = st_df[st_df["name"].str.contains(vacancy)]

    salary_lvl_year = {year: []}
    count_vac_year = {year: 0}
    salary_lvl_year_prof = {year: []}
    count_vac_year_prof = {year: 0}

    salary_lvl_year[year] = int(st_df['salary'].mean())
    count_vac_year[year] = len(st_df)
    salary_lvl_year_prof[year] = int(st_df_vacancy['salary'].mean())
    count_vac_year_prof[year] = len(st_df_vacancy)

    st_list = [salary_lvl_year, count_vac_year, salary_lvl_year_prof, count_vac_year_prof]
    queue.put(st_list)


if __name__ == "__main__":
    class UsersInput:
        def __init__(self):
            self.file_name = input('Введите название файла: ')
            self.vacancy_name = input("Введите название профессии: ")


    class GetCsvParts:
        def __init__(self, file_name):
            self.df = pd.read_csv(file_name)
            self.df['years'] = self.df['published_at'].apply(lambda s: s[:4])
            self.years = self.df['years'].unique()

            for year in self.years:
                data = self.df[self.df['years'] == year]
                data.iloc[:, :6].to_csv(rf'csv_files\part_{year}.csv', index=False)


    def sort_area_dict(dictionary):
        sorted_tuples = sorted(dictionary.items(), key=lambda item: item[1], reverse=True)[:10]
        sorted_dict = {k: v for k, v in sorted_tuples}
        return sorted_dict


    pd.set_option("expand_frame_repr", False)

    user_input = UsersInput()
    file, vacancy = user_input.file_name, user_input.vacancy_name
    csv_files = GetCsvParts(file)
    df = csv_files.df
    years = csv_files.years

    df['salary'] = df.loc[:, ['salary_from', 'salary_to']].mean(axis=1)
    df['published_at'] = df['published_at'].apply(lambda x: int(x[:4]))
    df_vacancy = df[df['name'].str.contains(vacancy)]

    total = len(df)
    df['count'] = df.groupby('area_name')['area_name'].transform('count')
    df_norm = df[df['count'] > 0.01 * total]
    cities = df_norm["area_name"].unique()

    salary_lvl_by_year, count_vac_by_year, salary_lvl_by_year_for_prof = {}, {}, {}
    count_vac_by_year_for_prof, salary_lvl_by_city, vacancy_rate_by_city = {}, {}, {}

    for city in cities:
        df_city = df_norm[df_norm['area_name'] == city]
        salary_lvl_by_city[city] = int(df_city['salary'].mean())
        vacancy_rate_by_city[city] = round(len(df_city) / len(df), 4)

    statistics = []
    queue = Queue()
    processes = []
    for year in years:
        process = Process(target=analysis_statistics, args=(vacancy, year, queue))
        processes.append(process)
        process.start()

    for process in processes:
        statistics = queue.get()
        salary_lvl_by_year.update(statistics[0])
        count_vac_by_year.update(statistics[1])
        salary_lvl_by_year_for_prof.update(statistics[2])
        count_vac_by_year_for_prof.update(statistics[3])
        process.join()

    print("Динамика уровня зарплат по годам:", salary_lvl_by_year)
    print("Динамика количества вакансий по годам:", count_vac_by_year)
    print("Динамика уровня зарплат по годам для профессии:", salary_lvl_by_year_for_prof)
    print("Динамика количества вакансий по годам для профессии:", count_vac_by_year_for_prof)
    print("Уровень зарплат по городам (в порядке убывания):", sort_area_dict(salary_lvl_by_city))
    print("Доля вакансий по городам (в порядке убывания):", sort_area_dict(vacancy_rate_by_city))
