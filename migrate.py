"""Clean a messy customers CSV and load it into MySQL.

Rows that cannot be fixed are not loaded: they are written to
output/rejected_rows.csv with the reason, and a summary is printed.
"""
import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import pandas as pd

INPUT_CSV = "data/customers_raw.csv"
REJECTED_CSV = "output/rejected_rows.csv"

# Day-first is assumed for dd/mm/yyyy dates (documented in the README).
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y"]
COUNTRY_MAP = {
    "colombia": "Colombia", "co": "Colombia",
    "spain": "Spain", "es": "Spain",
    "mexico": "Mexico", "mx": "Mexico",
}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def parse_date(value):
    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(value):
    text = str(value).replace("$", "").replace(",", "").strip()
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def clean_row(row):
    """Return (clean_dict, None) or (None, reason)."""
    name = " ".join(str(row["full_name"]).split()).title()
    if not name or name.lower() == "nan":
        return None, "missing name"

    email = str(row["email"]).strip().lower()
    if not EMAIL_RE.match(email):
        return None, "invalid or missing email"

    signup = parse_date(row["signup_date"])
    if signup is None:
        return None, "invalid date"

    country = COUNTRY_MAP.get(str(row["country"]).strip().lower())
    if country is None:
        return None, "unknown country"

    amount = parse_amount(row["total_spent"])
    if amount is None:
        return None, "invalid amount"

    return {"source_id": row["customer_id"], "full_name": name, "email": email, "signup_date": signup,
            "country": country, "total_spent": amount}, None


def clean_data(df):
    """Clean a raw DataFrame. Returns (clean_df, rejected_df)."""
    good, rejected = [], []
    for _, row in df.iterrows():
        cleaned, reason = clean_row(row)
        if cleaned is None:
            rejected.append({**row.to_dict(), "reject_reason": reason})
        else:
            good.append(cleaned)

    clean_df = pd.DataFrame(good)
    if not clean_df.empty:
        # Same email twice: keep the first row, reject the others.
        dup_mask = clean_df.duplicated(subset="email", keep="first")
        for _, row in clean_df[dup_mask].iterrows():
            info = row.to_dict()
            info["customer_id"] = info.pop("source_id")
            rejected.append({**info, "reject_reason": "duplicate email"})
        clean_df = clean_df[~dup_mask]
    return clean_df, pd.DataFrame(rejected)


def load_to_mysql(clean_df):
    import mysql.connector
    from dotenv import load_dotenv

    load_dotenv()
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
    )
    sql = """
        INSERT INTO customers (full_name, email, signup_date, country, total_spent)
        VALUES (%(full_name)s, %(email)s, %(signup_date)s, %(country)s, %(total_spent)s)
        ON DUPLICATE KEY UPDATE
            full_name = VALUES(full_name),
            signup_date = VALUES(signup_date),
            country = VALUES(country),
            total_spent = VALUES(total_spent)
    """
    cursor = conn.cursor()
    cursor.executemany(sql, clean_df.drop(columns="source_id").to_dict("records"))
    conn.commit()
    cursor.close()
    conn.close()


def main():
    raw = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)
    clean_df, rejected_df = clean_data(raw)

    os.makedirs("output", exist_ok=True)
    rejected_df.to_csv(REJECTED_CSV, index=False)
    load_to_mysql(clean_df)

    print("Migration report")
    print(f"  Rows read:     {len(raw)}")
    print(f"  Rows loaded:   {len(clean_df)}")
    print(f"  Rows rejected: {len(rejected_df)} (see {REJECTED_CSV})")
    if not rejected_df.empty:
        print(rejected_df["reject_reason"].value_counts().to_string())


if __name__ == "__main__":
    main()
