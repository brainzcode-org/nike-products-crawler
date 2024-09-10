# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NikeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NikeProductItems(scrapy.Item):
    name = scrapy.Field()
    colour = scrapy.Field()
    images = scrapy.Field()
    sku = scrapy.Field()
    url = scrapy.Field()
    brandName = scrapy.Field()

    # Pricing Information
    lowPrice = scrapy.Field()
    highPrice = scrapy.Field()
    priceCurrency = scrapy.Field()
    offerCount = scrapy.Field()

    # Availability
    availability = scrapy.Field()

    # Rating Information
    ratingValue = scrapy.Field()
    reviewCount = scrapy.Field()
    bestRating = scrapy.Field()
    worstRating = scrapy.Field()

    # Seller Information
    sellerName = scrapy.Field()
