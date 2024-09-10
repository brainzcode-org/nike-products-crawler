import json
import scrapy
from ..items import NikeProductItems


class NikeProductsSpider(scrapy.Spider):
    name = "nike_products"
    allowed_domains = ["www.nike.com", "api.nike.com"]

    def __init__(self, *args, **kwargs):
        super(NikeProductsSpider, self).__init__(*args, **kwargs)
        self.base_url = "https://www.nike.com/w/mens-tops-t-shirts-9om13znik1"
        self.api_url = "https://api.nike.com//discover/product_wall/v1/marketplace/US/language/en/consumerChannelId/d9a5bc42-4b9c-4976-858a-f159cf99c647"
        self.items_per_page = 24
        self.max_pages = 2  # Adjust this value to scrape more or fewer pages

    def start_requests(self):
        yield scrapy.Request(url=self.base_url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        product_links = response.css(
            "a.product-card__link-overlay::attr(href)"
        ).getall()

        for link in product_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(url=full_url, callback=self.parse_item)

        for page in range(self.max_pages):
            anchor = page * self.items_per_page
            api_url = f"{self.api_url}?path=/w/mens-tops-t-shirts-9om13znik1&attributeIds=0f64ecc7-d624-4e91-b171-b83a03dd8550,de314d73-b9c5-4b15-93dd-0bef5257d3b4&queryType=PRODUCTS&anchor={anchor}&count={self.items_per_page}"
            yield scrapy.Request(url=api_url, callback=self.parse_api_response)

    def parse_api_response(self, response):
        data = json.loads(response.text)
        products = data.get("data", {}).get("products", {}).get("objects", [])

        for product in products:
            product_url = f"https://www.nike.com/t/{product['slug']}"
            yield scrapy.Request(url=product_url, callback=self.parse_item)

    def parse_item(self, response):
        item = NikeProductItems()

        script_content = response.css('script[type="application/ld+json"]::text').get()
        product_data = json.loads(script_content)

        # Extracting product data
        item["name"] = product_data.get("name", "")
        # item["colour"] = product_data.get("color", "")
        item["images"] = json.dumps(product_data.get("image", []))
        item["sku"] = (
            product_data.get("sku", "") or response.url
        )  # Fallback to URL if SKU is missing
        item["url"] = response.url
        item["brandName"] = product_data.get("brand", {}).get("name", "")

        # Handle aggregate ratings with fallback for undefined values
        aggregate_rating = product_data.get("aggregateRating", {})
        item["ratingValue"] = self.parse_numeric_value(
            aggregate_rating.get("ratingValue")
        )
        item["reviewCount"] = self.parse_numeric_value(
            aggregate_rating.get("reviewCount")
        )
        item["bestRating"] = self.parse_numeric_value(
            aggregate_rating.get("bestRating")
        )
        item["worstRating"] = self.parse_numeric_value(
            aggregate_rating.get("worstRating")
        )

        # Handle pricing and availability in the AggregateOffer structure
        offers = product_data.get("offers", {})
        if isinstance(offers, dict) and offers.get("@type") == "AggregateOffer":
            # item["model"] = offer.get("itemOffered", {}).get("model", "")
            # item["color"] = offer.get("itemOffered", {}).get("color", "")
            item["lowPrice"] = offers.get("lowPrice")
            item["highPrice"] = offers.get("highPrice")
            item["priceCurrency"] = offers.get("priceCurrency")
            item["offerCount"] = offers.get("offerCount")
            item["availability"] = offers.get("availability", "")

            # Handling specific offers array
            first_offer = offers.get("offers", [{}])[
                0
            ]  # Take the first offer if available
            item["sellerName"] = first_offer.get("seller", {}).get("name", "")
        else:
            # Fallback if offers structure doesn't match AggregateOffer
            item["lowPrice"] = None
            item["highPrice"] = None
            item["priceCurrency"] = None
            item["offerCount"] = None
            item["availability"] = ""

        if "offers" in product_data:
            offers = product_data["offers"]
            if isinstance(offers, dict):
                offer = offers["offers"][0]
                # item["product_link"] = offer.get("url", "")
                # item["description"] = offer.get("itemOffered", {}).get("description", "")
                # item["model"] = offer.get("itemOffered", {}).get("model", "")
                item["colour"] = offer.get("itemOffered", {}).get("color", "") or None
                # item["price"] = offer.get("price", 0)

        yield item

    def parse_numeric_value(self, value):
        """Helper function to safely parse numeric values from JSON-LD data."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
