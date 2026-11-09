import asyncio
import random
from pathlib import Path
from sqlalchemy import text
from app.services.database import engine

REGIONS = ["华东", "华南", "华北", "西部"]
PRODUCTS = ["企业版", "专业版", "基础版", "增值服务"]
MONTHS = [f"2026-{month:02d}" for month in range(1, 10)]

async def seed() -> None:
    Path("./data").mkdir(exist_ok=True)

    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales_metrics (
                id INTEGER PRIMARY KEY,
                year INTEGER NOT NULL,
                month VARCHAR(7) NOT NULL,
                region VARCHAR(20) NOT NULL,
                product VARCHAR(50) NOT NULL,
                sales_amount NUMERIC NOT NULL,
                gross_profit NUMERIC NOT NULL,
                order_count INTEGER NOT NULL
            )
        """))

        existing = (await conn.execute(text("SELECT COUNT(*) FROM sales_metrics"))).scalar_one()
        if existing:
            print(f"sales_metrics already seeded: {existing} rows")
            return

        rng = random.Random(42)
        row_id = 1
        rows = []
        region_factor = {"华东": 1.35, "华南": 1.12, "华北": 0.96, "西部": 0.72}
        product_factor = {"企业版": 1.45, "专业版": 1.20, "基础版": 0.82, "增值服务": 0.55}

        for month_index, month in enumerate(MONTHS, start=1):
            season = 0.92 + month_index * 0.025
            for region in REGIONS:
                for product in PRODUCTS:
                    base = 800_000 * region_factor[region] * product_factor[product] * season
                    sales = round(base * rng.uniform(0.88, 1.12), 2)
                    profit = round(sales * rng.uniform(0.22, 0.38), 2)
                    orders = int(max(50, sales / rng.uniform(5500, 9000)))
                    rows.append({
                        "id": row_id,
                        "year": 2026,
                        "month": month,
                        "region": region,
                        "product": product,
                        "sales_amount": sales,
                        "gross_profit": profit,
                        "order_count": orders,
                    })
                    row_id += 1

        insert_sql = text("""
            INSERT INTO sales_metrics
            (id, year, month, region, product, sales_amount, gross_profit, order_count)
            VALUES
            (:id, :year, :month, :region, :product, :sales_amount, :gross_profit, :order_count)
        """)
        await conn.execute(insert_sql, rows)
        print(f"seeded {len(rows)} rows")

if __name__ == "__main__":
    asyncio.run(seed())
