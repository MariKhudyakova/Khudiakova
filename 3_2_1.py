import pandas as pd


pd.set_option("expand_frame_repr", False)
file = "vacancies_by_year.csv"
df = pd.read_csv(file)
df['years'] = df['published_at'].apply(lambda s: s[:4])
years = df['years'].unique()
for year in years:
    data = df[df['years'] == year]
    data.iloc[:, :6].to_csv(rf'csv_files\part_{year}.csv', index=False)