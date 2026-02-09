import pandas as pd

df = pd.read_csv("FactResellerSales.csv", sep="|")
print(len(df.columns))
print(df)   