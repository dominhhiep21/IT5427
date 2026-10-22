"""Cleaning for products and the category translation table."""

from __future__ import annotations

import pandas as pd

from src.clean.common import to_numeric


def clean_translation(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["product_category_name"] = out["product_category_name"].astype("string").str.strip()
    out["product_category_name_english"] = (
        out["product_category_name_english"].astype("string").str.strip()
    )
    return out


def clean_products(df: pd.DataFrame, translation: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    numeric_columns = (
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    )
    for column in numeric_columns:
        out[column] = to_numeric(out[column])

    category = out["product_category_name"].astype("string").str.strip()
    out["category_missing"] = category.isna() | (category == "")
    out["product_category_name"] = category.mask(out["category_missing"], "unknown")

    translation = translation.rename(
        columns={
            "product_category_name": "product_category_name",
            "product_category_name_english": "product_category_name_english",
        }
    )
    merged = out.merge(
        translation[["product_category_name", "product_category_name_english"]],
        on="product_category_name",
        how="left",
    )
    merged["translation_missing"] = (
        ~merged["category_missing"] & merged["product_category_name_english"].isna()
    )
    merged["product_category_name_english"] = merged[
        "product_category_name_english"
    ].fillna(merged["product_category_name"])
    return merged
