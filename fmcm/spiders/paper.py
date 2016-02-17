# -*- coding: utf-8 -*-

import codecs

from scrapy.spiders import Spider
from scrapy.selector import Selector

from fmcm.items import FmcmItem


class PaperSpider(Spider):

    name = 'paper'
    allowed_domins = ['thepaper.cn']
    start_urls = ['http://www.thepaper.cn', ]

    def parse(self, response):
        try:
            sel = Selector(response)
            # import pdb; pdb.set_trace()
            name = response.url.split('/')[-2]
            if name:
                file_name = '%s.html' % name
            else:
                file_name = 'home_page.html'
            with open(file_name, 'w') as f:
                f.write(response.body)
            hot_list = sel.xpath('//*[@class="list_hot"]')
            items = []
            with codecs.open('article_list.txt', 'w', 'utf-8') as f:
                count = 1
                for article_list in hot_list:
                    for article in article_list.xpath('li'):
                        item = FmcmItem()
                        title = article.xpath('a/text()').extract()
                        url = article.xpath('a/attribute::href').extract()
                        if not title:
                            continue
                        if not url:
                            url = ''
                        item['title'] = title[0]
                        item['url'] = url[0]
                        items.append(item)
                        f.write('%s. ' % count)
                        count += 1
                        f.write('title: %s\n    url: %s\n' % (title[0], url[0]))
        except Exception as e:
            import pdb; pdb.set_trace()

        return items
