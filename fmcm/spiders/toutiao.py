# -*-coding: utf-8 -*-

from scrapy.spiders import Spider
from scrapy.selector import Selector

from fmcm.items  import FmcmItem


class ToutiaoSpider(Spider):

    name = 'toutiao'
    allowed_domins = ['toutiao.com']
    start_urls = ['http://www.toutiao.com', ]

    def parse(self, response):
        sel = Selector(response)
        article_list = sel.xpath('//*[@id="pagelet-feedlist"]/ul/li')
        import pdb; pdb.set_trace()
        items = []

        for article in article_list:
            item = FmcmItem()
            item['title'] = article.xpath('div/p/a/text()').extract()
            print item['title']
            items.append(item)

        return items
