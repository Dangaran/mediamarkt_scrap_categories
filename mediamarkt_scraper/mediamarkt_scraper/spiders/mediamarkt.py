# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import time
import logging
from mediamarkt_scraper.items import item_info


class Mediamarkt_Spider(scrapy.Spider):
    name = 'mediamarkt'
    allowed_domains = ['mediamarkt.es']
    start_urls = ['https://www.mediamarkt.es']

    def parse(self, response):
        # select categories and their url.
        onclick = response.xpath('//*[contains(@class, "distributor-img")]/@onclick').extract()
        general_categories = {'categories': [item.split("> ")[1].split("'")[0] for item in onclick],
                              'url': [item.split("'")[1] for item in onclick]}
        try:
            # Ask which category should be scrapped
            input_cat = input('Choose the category that you want to scrap:\n{}\n'.format(', '.join(general_categories['categories']))).strip()
            cat_index = general_categories['categories'].index(str(input_cat))

        except ValueError:
            input_cat = input('Wrong category, please copy and paste the same name from this list:\n{}\n'.format(', '.join(general_categories['categories']))).strip()
            print(input_cat)
            cat_index = general_categories['categories'].index(str(input_cat))

        url_to_scrap = general_categories['url'][cat_index]
        # request to url
        yield Request(url_to_scrap, callback=self._get_subcategories, meta={'url': url_to_scrap})

    def _get_subcategories(self, response):
        # if category has subcategories, let the user choose a new one, if not extract products from that category
        response_sub_cat = response.xpath('//*[@class="worldDistributor"]')
        if response_sub_cat:
            sub_cat = response_sub_cat.xpath('.//*[contains(@class, "distributor-")]/img/@alt').extract()
            subcat = {
                'sub_category': sub_cat,
                'url': response_sub_cat.xpath('.//article/a[contains(@class, "distributor-")]/@href').extract()
            }
            try:
                input_subcat = input('This product has subcategories. Please, select one from the list:\n{}\n'.format(', '.join(subcat['sub_category']))).strip()
                subcat_index = subcat['sub_category'].index(input_subcat)
            except ValueError:
                input_subcat = input('Wrong category, please copy and paste the same name from this list:\n{}\n'.format(', '.join(subcat['sub_category']))).strip()
                subcat_index = subcat['sub_category'].index(input_subcat)
            url_to_scrap = subcat['url'][subcat_index]
            # request to url
            yield Request(url_to_scrap, callback=self._get_products, dont_filter=True)

        else:
            url_to_category = response.meta['url']
            print('no subcategories found')
            yield Request(url_to_category, callback=self._get_products, dont_filter=True)

    def _get_products(self, response):
        third_category = response.xpath('//*[@class="categories-flat-descendants"]')
        if third_category:
            for new_cat in third_category.xpath('.//a/@href').extract():
                url_new_cat = self.start_urls[0] + new_cat
                yield Request(url_new_cat, callback=self._get_products, dont_filter=True)
        else:
            # extract information for each product
            for product in response.xpath('//*[@class="product-wrapper"]'):
                # set item variable to fill
                product_info = {}
                try:
                    # extract link to product
                    incomplete_link = product.xpath('.//*[@class="photo clickable"]/@data-clickable-href').extract()
                    product_info['product_link'] = ['www.mediamarkt.es' + link for link in incomplete_link]
                    # extract and parse product name
                    product_info['product_name'] = product.xpath('.//*[@class="content "]/h2/a/text()').extract_first().replace('\r\n\t\t\t\t', '')
                    # product_name = [item.split('- ')[1] for item in product_name_extracted if item.find('- ') != -1]
                    # extract brand of the product
                    try:
                        product_info['brand_name'] = product.xpath('.//*[@class="manufacturer clickable"]/img[@alt]/@alt').extract_first()
                    except:
                        product_info['brand_name'] = 'No brand found'
                    # extract product specs
                    specs = product.xpath('.//*[@class="product-details"]/dt/text()').extract()
                    for number in range(len(specs)):
                        product_info.update({str(specs[number].replace(':', '')): product.xpath('.//*[@class="product-details"]/dd["style"][{}]/text()'.format(number+1)).extract_first()})
                    # extract actual price
                    product_info['actual_price'] = product.xpath('.//*[@class="price small"]/text()').extract_first().split('-')[0].replace(',', '.')
                    # sale_item?
                    product_info['sale_item'] = False
                    if product.xpath('.//*[@class="price-old-info price-old-info-text"]').extract():
                        product_info['sale_item'] = True

                    yield product_info
                except:
                    logging.warning('Skip this product due to error')
                    pass

            # if actual page has pagination, change to next page
            path = response.xpath('//*[@class="pagination-next"]/a[@href]/@href').extract_first()
            time.sleep(2)
            if path:
                print('Scraping next page')
                url_next_page = 'https://www.mediamarkt.es{}'.format(path)
                yield Request(url_next_page, callback=self._get_products)
