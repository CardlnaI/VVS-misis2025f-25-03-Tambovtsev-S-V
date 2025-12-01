import pandas as pd
import numpy as np
import sys

CSV_PATH = "tested.csv"

def load_data(path):
    return pd.read_csv(path)

def analyze_missing(df):
    return int(df.isnull().sum().sum())

def print_column_info(df):
    print(df.dtypes)

def show_head(df, n):
    print(df.head(n))

def describe_numeric(df):
    print(df.describe())

def print_shape(df):
    print(df.shape)

def compute_survival_stats(df):
    required = {"Survived", "Age"}
    if not required.issubset(df.columns):
        print("Не хватает столбцов для анализа.")
        return

    value_counts = df['Survived'].value_counts(normalize=True)
    survived_pct = value_counts.get(1, 0) * 100
    print(f"Процент выживших: {survived_pct:.2f}%")

    overall_avg_age = df['Age'].mean()
    avg_age_survived = df[df['Survived'] == 1]['Age'].mean()
    avg_age_died = df[df['Survived'] == 0]['Age'].mean()

    print(f"Средний возраст (всего): {overall_avg_age:.2f}")
    print(f"Средний возраст выживших: {avg_age_survived:.2f}")
    print(f"Средний возраст умерших: {avg_age_died:.2f}")

def create_summary_table(df):
    needed = {"Sex", "Pclass", "Age", "Fare", "Survived"}
    if not needed.issubset(df.columns):
        return None

    cleaned = df.dropna(subset=list(needed))

    grouped = cleaned.groupby(['Sex', 'Pclass'], as_index=False).agg(
        mean_age=('Age', 'mean'),
        mean_fare=('Fare', 'mean'),
        survived_pct=('Survived', lambda x: x.mean() * 100)
    )

    grouped['mean_age'] = grouped['mean_age'].round(2)
    grouped['mean_fare'] = grouped['mean_fare'].round(2)
    grouped['survived_pct'] = grouped['survived_pct'].round(2)

    return grouped.rename(columns={
        'mean_age': 'Mean age',
        'mean_fare': 'Mean fare',
        'survived_pct': 'Survived (%)'
    })


df = load_data(CSV_PATH)
print(df)
print('---------------------------------')

missing = analyze_missing(df)
print(f"Всего пропусков: {missing}")

print_column_info(df)

n = int(input("Введите количество строк: "))
show_head(df, n)

describe_numeric(df)
print_shape(df)

print('---------------------------------')

compute_survival_stats(df)

summary = create_summary_table(df)
print(summary)
