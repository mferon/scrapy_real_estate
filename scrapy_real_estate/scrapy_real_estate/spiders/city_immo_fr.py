# -*- coding: utf-8 -*-
import logging
import scrapy
import re


class CityImmoFrSpider(scrapy.Spider):
    name = 'city-immo.fr'
    site_base = 'http://www.city-immo.fr/site/'
    fail = False

    def start_requests(self):
        urls = [
            f'nos-biens-immobiliers.php?annonce_transaction=ventes&type_nom=maisons-fermes&ville_slug=null&budget_min={self.config["offers"]["min_price"]}&budget_max={self.config["offers"]["max_price"]}&annonce_reference=&button=',
        ]
        for url in urls:
            yield scrapy.Request(url=f'{self.site_base}{url}', callback=self.parse, errback=self.errback)

    def parse(self, response):
        links = scrapy.linkextractors.LinkExtractor(restrict_css='a.bien').extract_links(response)
        for link in links:
            yield {
                'url': link.url,
                'description': re.sub(r'\s+', ' ', link.text),
            }

    def errback(self, failure):
        self.fail = True
