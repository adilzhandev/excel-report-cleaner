"""
Очистка грязной табличной выборки (data/raw_data.csv) и выгрузка
результата в Excel-отчёт (report.xlsx) с очищенными данными и сводкой.
"""

import pandas as pd

RAW_PATH = "data/raw_data.csv"
REPORT_PATH = "report.xlsx"


def load_raw(path: str) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str)


# Курсы приходят в разном регистре ("Excel продвинутый" / "excel ПРОДВИНУТЫЙ").
# .capitalize() тут не подходит — испортит "SQL" в "Sql". Поэтому явный
# словарь: ключ — нормализованное (lower+strip) название, значение — как
# должно выглядеть в отчёте.
CANONICAL_COURSES = {
    "python для анализа данных": "Python для анализа данных",
    "sql для начинающих": "SQL для начинающих",
    "excel продвинутый": "Excel продвинутый",
}


def normalize_text(df: pd.DataFrame) -> pd.DataFrame:
    """Убирает лишние пробелы у full_name и приводит course к каноническому виду."""
    df = df.copy()
    df["full_name"] = df["full_name"].str.strip()

    course_key = df["course"].str.strip().str.lower()
    df["course"] = course_key.map(CANONICAL_COURSES).fillna(df["course"].str.strip())
    return df


if __name__ == "__main__":
    df = load_raw(RAW_PATH)
    print(f"Прочитано строк: {len(df)}")

    df = normalize_text(df)
    print(df[["full_name", "course"]].head(10))
