#!/usr/bin/env python3
"""
Query actual products from the database
"""
import sqlite3
from pathlib import Path
from database_config import DATABASE_PATH

DB_PATH = DATABASE_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("📦 PRODUCTS IN DATABASE")
print("=" * 80)

# Get total count
cursor.execute("SELECT COUNT(*) FROM product_data")
total = cursor.fetchone()[0]
print(f"\n✅ Total products: {total}\n")

# Get first 20 products
print("First 20 products:")
print("-" * 80)
cursor.execute("""
    SELECT 
        id,
        name, 
        part_number,
        sale_price,
        currency,
        country,
        brand,
        extraction_date
    FROM product_data
    LIMIT 20
""")

for i, row in enumerate(cursor.fetchall(), 1):
    product_id, name, part_number, price, currency, country, brand, date = row
    print(f"{i:2d}. {name}")
    print(
        f"    Part#: {part_number} | Price: {price} {currency} | Country: {country}")
    print()

print("-" * 80)

# Get summary by country
print("\n📊 SUMMARY BY COUNTRY:")
print("-" * 80)
cursor.execute("""
    SELECT country, COUNT(*) as count
    FROM product_data
    GROUP BY country
    ORDER BY count DESC
""")

for country, count in cursor.fetchall():
    print(f"  {country}: {count} products")

print()

# Get summary by brand
print("📊 SUMMARY BY BRAND (Top 10):")
print("-" * 80)
cursor.execute("""
    SELECT brand, COUNT(*) as count
    FROM product_data
    WHERE brand IS NOT NULL
    GROUP BY brand
    ORDER BY count DESC
    LIMIT 10
""")

for brand, count in cursor.fetchall():
    print(f"  {brand}: {count} products")

print()

# Get summary by run
print("📊 SUMMARY BY RUN:")
print("-" * 80)
cursor.execute("""
    SELECT run_token, COUNT(*) as count
    FROM product_data
    GROUP BY run_token
    ORDER BY count DESC
""")

for run_token, count in cursor.fetchall():
    print(f"  {run_token}: {count} products")

print("\n" + "=" * 80)

conn.close()
