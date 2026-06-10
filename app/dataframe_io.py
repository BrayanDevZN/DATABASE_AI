from datetime import date, datetime
from io import BytesIO
import math

import polars as pl


def make_json_safe(value):
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    if isinstance(value, tuple):
        return [make_json_safe(item) for item in value]

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None

    if hasattr(value, "item"):
        try:
            return make_json_safe(value.item())
        except Exception:
            return value

    return value


def _drop_empty_rows(df: pl.DataFrame) -> pl.DataFrame:
    if df.is_empty() or not df.columns:
        return df

    return df.filter(pl.any_horizontal(pl.all().is_not_null()))


def _normalize_df(df: pl.DataFrame) -> pl.DataFrame:
    df = df.rename({column: str(column).strip() for column in df.columns})
    return _drop_empty_rows(df)


def dataframe_to_records(df: pl.DataFrame) -> tuple[list[dict], int, int]:
    df = _normalize_df(df)
    records = make_json_safe(df.to_dicts())
    return records, df.height, df.width


def rows_to_records(rows) -> tuple[list[dict], int, int]:
    if isinstance(rows, dict):
        for key in ("data", "results", "items", "rows", "products", "users"):
            if isinstance(rows.get(key), list):
                rows = rows[key]
                break
        else:
            rows = [rows]

    if not isinstance(rows, list):
        raise ValueError("A fonte precisa retornar uma lista de registros.")

    if not rows:
        return [], 0, 0

    return dataframe_to_records(pl.from_dicts(rows, infer_schema_length=None))


def read_uploaded_content(content: bytes, filename: str) -> tuple[list[dict], int, int]:
    lower_filename = filename.lower()

    if lower_filename.endswith(".csv"):
        return dataframe_to_records(pl.read_csv(BytesIO(content), infer_schema_length=1000))

    if lower_filename.endswith(".json"):
        return dataframe_to_records(pl.read_json(BytesIO(content)))

    if lower_filename.endswith(".xlsx") or lower_filename.endswith(".xls"):
        import pandas as pd

        df = pd.read_excel(BytesIO(content))
        return rows_to_records(df.to_dict(orient="records"))

    raise ValueError("Formato invalido. Envie CSV, XLSX, XLS ou JSON.")
