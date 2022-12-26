import pandas as pd
import requests

pd.set_option("expand_frame_repr", False)
df = pd.read_csv("vacancies_dif_currencies.csv")

df_currency_counter = df.groupby("salary_currency").size()
df_currency_counter = df_currency_counter[df_currency_counter > 5000]

first_month_2003 = int(".".join(df["published_at"].min()[5:7].split("-")))
last_month_2022 = int(".".join(df["published_at"].max()[5:7].split("-")))

df_api_currency = pd.DataFrame(columns=["date", "BYR", "USD", "EUR", "KZT", "UAH"])

i = 0
for year in range(2003, 2023):
    first_month = first_month_2003 if year == 2003 else 1
    last_month = last_month_2022 + 1 if year == 2022 else 13
    for month in range(first_month, last_month):
        date = f'0{month}/{year}' if month < 10 else f'{month}/{year}'
        url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{date}d=1"
        response = requests.get(url)
        currency_df = pd.read_xml(response.text)
        currency_filtered_df = currency_df.loc[currency_df['CharCode'].isin(["BYN", "BYR", "EUR", "KZT", "UAH", "USD"])]

        BYR = float(currency_filtered_df.loc[currency_filtered_df['CharCode'].isin(['BYR', 'BYN'])]['Value'].values[0].replace(',', '.')) / (currency_filtered_df.loc[currency_filtered_df['CharCode'].isin(['BYR', 'BYN'])]['Nominal'].values[0])
        USD = float(currency_filtered_df.loc[currency_filtered_df['CharCode'] == 'USD']['Value'].values[0].replace(',', '.')) / (currency_filtered_df.loc[currency_filtered_df['CharCode'] == 'USD']['Nominal'].values[0])
        EUR = float(currency_filtered_df.loc[currency_filtered_df['CharCode'] == 'EUR']['Value'].values[0].replace(',', '.')) / (currency_filtered_df.loc[currency_filtered_df['CharCode'] == 'EUR']['Nominal'].values[0])
        KZT = float(currency_filtered_df.loc[currency_filtered_df['CharCode'] == 'KZT']['Value'].values[0].replace(',', '.')) / (currency_filtered_df.loc[currency_filtered_df['CharCode'] == 'KZT']['Nominal'].values[0])
        UAH = float(currency_filtered_df.loc[currency_filtered_df['CharCode'] == 'UAH']['Value'].values[0].replace(',', '.')) / (currency_filtered_df.loc[currency_filtered_df['CharCode'] == 'UAH']['Nominal'].values[0])

        df_api_currency.loc[i] = [date, BYR, USD, EUR, KZT, UAH]
        i += 1

df_api_currency.to_csv("сurrency_data.csv", index=False)
print(df_api_currency)
