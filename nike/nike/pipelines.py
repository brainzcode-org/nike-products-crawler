from itemadapter import ItemAdapter
import sqlite3


class NikePipeline:
    def process_item(self, item, spider):
        return item


class DataStandardizationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Standardize availability
        if adapter.get("availability") == "https://schema.org/InStock":
            adapter["availability"] = "InStock"

        # Convert lowPrice and highPrice to float
        low_price = adapter.get("lowPrice")
        high_price = adapter.get("highPrice")

        if low_price is not None:
            try:
                adapter["lowPrice"] = float(low_price)
            except ValueError:
                adapter["lowPrice"] = None

        if high_price is not None:
            try:
                adapter["highPrice"] = float(high_price)
            except ValueError:
                adapter["highPrice"] = None

        # Ensure numeric fields are the correct type
        for field in ["ratingValue", "reviewCount", "bestRating", "worstRating"]:
            value = adapter.get(field)
            if value is not None:
                try:
                    adapter[field] = float(value)
                except ValueError:
                    adapter[field] = None

        return item


class SQLitePipeline:
    def __init__(self):
        self.conn = sqlite3.connect("nike_products.db")
        self.cur = self.conn.cursor()

        # Create the 'products' table with the updated fields
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                name TEXT,
                colour TEXT,
                images TEXT,
                sku TEXT,
                url TEXT,
                availability TEXT,
                lowPrice REAL,
                highPrice REAL,
                priceCurrency TEXT,
                offerCount INTEGER,
                brandName TEXT,
                ratingValue REAL,
                reviewCount INTEGER,
                bestRating REAL,
                worstRating REAL,
                sellerName TEXT
            )
        """)

    def process_item(self, item, spider):
        # Ensure all fields exist and have values (None if not present)
        required_fields = [
            "name",
            "colour",
            "images",
            "sku",
            "url",
            "availability",
            "lowPrice",
            "highPrice",
            "priceCurrency",
            "offerCount",
            "brandName",
            "ratingValue",
            "reviewCount",
            "bestRating",
            "worstRating",
            "sellerName",
        ]

        # Set default value of None for missing fields
        for field in required_fields:
            if field not in item:
                item[field] = None

        # Check if the item is already in the database
        self.cur.execute("SELECT * FROM products WHERE sku = ?", (item["sku"],))
        result = self.cur.fetchone()

        if result:
            spider.logger.warn(f"Item already in DB: {item['sku']}")
        else:
            # Insert the new item into the database
            self.cur.execute(
                """
                INSERT INTO products(
                    name, colour, images, sku, url,
                    availability, lowPrice, highPrice, priceCurrency, offerCount,
                    brandName, ratingValue, reviewCount, bestRating, worstRating,
                    sellerName
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item["name"],
                    item["colour"],
                    item["images"],
                    item["sku"],
                    item["url"],
                    item["availability"],
                    item["lowPrice"],
                    item["highPrice"],
                    item["priceCurrency"],
                    item["offerCount"],
                    item["brandName"],
                    item["ratingValue"],
                    item["reviewCount"],
                    item["bestRating"],
                    item["worstRating"],
                    item["sellerName"],
                ),
            )
            self.conn.commit()

        return item

    def close_spider(self, spider):
        self.conn.close()
