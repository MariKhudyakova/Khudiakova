import pandas as pd
import sqlite3

df = pd.read_csv('currency_date.csv')

connection = sqlite3.connect('currency_date.db')
cursor = connection.cursor()
df.to_sql(name="currency_date", con=connection, if_exists='replace', index=False)
connection.commit()
