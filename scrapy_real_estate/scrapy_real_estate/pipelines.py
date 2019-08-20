# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import configparser
import json
import logging
import os
import smtplib
from email.mime.text import MIMEText


class ScrapyRealEstatePipeline(object):
    def open_spider(self, spider):
        self.config = configparser.ConfigParser()
        self.config.read('scrapy_real_estate.cfg')
        spider.config = self.config
        self.offers = {}

    def close_spider(self, spider):
        if spider.fail:
            logging.warning('Spider fails, do not do anything')
            return

        data_dir = 'offers_data'

        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)

        filename = os.path.join(data_dir, f'{spider.name}_items.json')

        try:
            with open(filename) as fh:
                last_offers = set(json.load(fh))
        except Exception:
            last_offers = set()

        new_offers = self.offers.keys() - last_offers

        if new_offers:
            logging.info(f'/!\\ /!\\ New offers: {new_offers} /!\\ /!\\')
            self.send_mail(new_offers, spider)

        with open(filename, 'w') as fh:
            json.dump(list(self.offers.keys()), fh)

    def process_item(self, item, spider):
        self.offers[item['url']] = item
        return item

    def send_mail(self, new_offers, spider):
        new_offers_str = "\r\n\r\n\r\n".join(['{0}\r\n{1}'.format(offer['url'], offer['description']) for offer in self.offers.values() if offer['url'] in new_offers])

        content = f"""
Hey!

Here are new {spider.name} offers:

{new_offers_str}
"""

        msg = MIMEText(content, _charset="UTF-8")
        msg['Subject'] = f'New offers at {spider.name} !'
        msg['From'] = self.config['smtp'].get('from') or self.config['smtp']['user']
        msg['To'] = self.config['smtp']['to']

        with smtplib.SMTP_SSL(host=self.config['smtp']['host'], port=self.config['smtp']['port']) as s:
            s.login(self.config['smtp']['user'], self.config['smtp']['password'])
            s.send_message(msg)
