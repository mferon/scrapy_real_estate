# -*- coding: utf-8 -*-
import logging
import scrapy
import re


class CityImmoFrSpider(scrapy.Spider):
    name = 'reference-immobiliere.com'
    site_base = 'http://www.reference-immobiliere.com/'
    fail = False

    def start_requests(self):
        urls = [
            f'ventes.php?Ville=&PrixMini={self.config["offers"]["min_price"]}&PrixMaxi={self.config["offers"]["max_price"]}&Categorie=Maison&Ref=',
        ]
        for url in urls:
            yield scrapy.Request(url=f'{self.site_base}{url}', callback=self.parse, errback=self.errback)

    def parse(self, response):
        for offer in response.css('div.col-md-3'):
            if offer.css('div.VenduLoue'):
                continue

            a_tag = offer.css('a.hover-img')
            if not a_tag:
                continue

            url = response.urljoin(a_tag.attrib['href'])
            description = offer.css('h4::text').getall()

            yield {
                'url': url,
                'description': ' - '.join(description),
            }

        select_next = False
        next_page = None
        for li in response.css('ul.pagination li'):
            if select_next:
                next_page = li.css('a')[0]
                break
            if li.attrib.get('class') == 'active':
                select_next = True
                continue

        if next_page:
            logging.critical(next_page)
            yield response.follow(next_page, callback=self.parse, errback=self.errback)

    def errback(self, failure):
        self.fail = True
