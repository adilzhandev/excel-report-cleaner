"""
Очистка грязной табличной выборки (data/raw_data.csv) и выгрузка
результата в Excel-отчёт (report.xlsx) с очищенными данными и сводкой.
"""

import pandas as pd

RAW_PATH = "data/raw_data.csv"
REPORT_PATH = "report.xlsx"


def load_raw(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str)


if __name__ == "__main__":
    df = load_raw(RAW_PATH)
    print(f"Прочитано строк: {len(df)}")
    print(df.head())
