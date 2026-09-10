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


# В датасете дата приходит в трёх форматах: 2024-01-15, 15.01.2024, 2024/01/16.
# pandas.to_datetime с format=None угадывает не всегда стабильно (может
# перепутать день/месяц), поэтому пробуем форматы по очереди явно.
DATE_FORMATS = ["%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"]


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    parsed = pd.Series(pd.NaT, index=df.index)
    for fmt in DATE_FORMATS:
        mask = parsed.isna()
        parsed[mask] = pd.to_datetime(df.loc[mask, "enrollment_date"], format=fmt, errors="coerce")
    df["enrollment_date"] = parsed.dt.strftime("%Y-%m-%d")
    return df


def normalize_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """Приводит score/attendance_pct к числам и обнуляет значения вне 0-100.

    score=120 или score=-5 — это ошибки ввода (баллы физически не могут
    быть больше 100 или отрицательными), а не реальные оценки. Не
    удаляем всю строку из-за одного плохого числа — только помечаем
    само значение как пропущенное (NaN), остальные данные строки годные.
    """
    df = df.copy()
    for col in ("score", "attendance_pct"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
        out_of_range = ~df[col].between(0, 100)
        df.loc[out_of_range, col] = pd.NA
    return df


if __name__ == "__main__":
    df = load_raw(RAW_PATH)
    print(f"Прочитано строк: {len(df)}")

    df = normalize_text(df)
    df = normalize_dates(df)
    df = normalize_numbers(df)
    print(df[["full_name", "course", "enrollment_date", "score", "attendance_pct"]])
    print("Не распознанных дат:", df["enrollment_date"].isna().sum())
    print("Пропущенных score:", df["score"].isna().sum())
