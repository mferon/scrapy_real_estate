# -*- coding: utf-8 -*-
import logging
import scrapy
import re
import urllib


class DeleuimmobilierComSpider(scrapy.Spider):
    name = 'deleuimmobilier.com'
    site_base = 'https://www.deleuimmobilier.com/'
    fail = False

    def start_requests(self):
        urls = [
            f'recherche',
        ]

        post_data = {
            '_method': 'POST',
            'data[Recherche][type]': '1',
            'data[Recherche][prix]': self.config['offers']['min_price'],
            'data[Recherche][secteurs]': '',
            'data[Recherche][ref]': '',
            'recherchebiens': 'Valider',
        }

        post_data_str = '&'.join([f'{urllib.parse.quote(k)}={v}' for k, v in post_data.items()])

        for url in urls:
            yield scrapy.Request(
                url=f'{self.site_base}{url}',
                method='POST',
                callback=self.parse,
                errback=self.errback,
                body=post_data_str,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
            )

    def parse(self, response):
        for offer in response.css('div.bloc_acc_nouv_cont2'):
            if offer.css('div.bloc_acc_vendu_title'):
                continue

            a_tag = offer.css('a')
            if not a_tag:
                continue

            url = response.urljoin(a_tag.attrib['href'])
            price_str = offer.css('div.bloc_acc_nouv_prix::text').get()
            city = offer.css('div.bloc_acc_nouv_title::text').get()

            try:
                price = int(re.sub(r'[^0-9]', '', price_str))
                if price > int(self.config['offers']['max_price']):
                    # Too expensive
                    continue
            except ValueError:
                pass

            yield {
                'url': url,
                'description': f'{city} - {price_str}',
            }

        next_page = None
        for a_tag in response.css('a.result_pagination_next'):
            if a_tag.attrib['title'] == 'Page suivante':
                next_page = response.urljoin(a_tag.attrib['href'])
                break

        if next_page:
            yield response.follow(next_page, callback=self.parse, errback=self.errback)

    def errback(self, failure):
        self.fail = True
