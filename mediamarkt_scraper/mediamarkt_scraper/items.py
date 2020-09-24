# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class item_info(scrapy.Item):
    brand_name = scrapy.Field()
    product_name = scrapy.Field()
    actual_price = scrapy.Field()
    sale_item = scrapy.Field()
    product_link = scrapy.Field()
    #specs = scrapy.Field()
