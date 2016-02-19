# -*- coding: utf-8 -*-

import codecs

from scrapy import Request
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
            count = 1
            for article_list in hot_list:
                for article in article_list.xpath('li'):
                    item = {}
                    title = article.xpath('a/text()').extract()
                    url = article.xpath('a/attribute::href').extract()
                    # import pdb; pdb.set_trace()
                    if not title:
                        continue
                    if not url:
                        url = ''
                    else:
                        url = response.urljoin(url[0])
                    item['list_title'] = title[0]
                    item['url'] = url
                    item['count'] = count
                    count += 1
                    # f = codecs.open('article_list.txt', 'a', 'utf-8')
                    # f.write('%s. ' % count)
                    # f.write(
                    #     'title: %s\n    url: %s\n' % (title[0], url))
                    # f.flush()

                    # for news detail process
                    request = Request(url, callback=self.parse_news_detail)
                    request.meta.update(item)
                    yield request
        except Exception as e:
            import pdb; pdb.set_trace()

        # return items

    def parse_news_detail(self, response):
        # import pdb; pdb.set_trace()
        try:
            sel = Selector(response)
            title = sel.xpath('//*[@class="news_title"]/text()').extract()
            news_abouts = sel.xpath('//*[@class="news_about"]/p')
            news_about = ''
            for text in news_abouts:
                s = text.xpath('text()').extract()
                if s:
                    # import pdb; pdb.set_trace()
                    news_about = '%s\n%s' % (news_about, s[0])
            s = news_abouts[-1].xpath('a/text()').extract()
            news_about = '%s%s' % (news_about, s[0])
            # import pdb; pdb.set_trace()
            content = sel.xpath('//*[@class="news_txt"]').extract()
            news_editor = sel.xpath(
                '//*[@class="news_editor"]/text()').extract()
            news_keyword = sel.xpath(
                '//*[@class=news_keyword]/text()').extract()
            zan = sel.xpath('//*[@id="zan"]/text()').extract()
            title = ''.join(title)
            content = ''.join(content)
            news_editor = ''.join(news_editor)
            news_keyword = ''.join(news_keyword)
            zan = zan[0] if zan else ''
            with codecs.open('article_detail.txt', 'a', 'utf-8') as f:
                f.write(
                    '%s.  %s\n%s\n%s\n%s  zan:%s%s\n%s\n%s\n\n\n' %
                    (response.meta['count'], response.meta['list_title'],
                        response.meta['url'], title, news_editor, zan,
                        news_about, news_keyword, content)
                )
        except Exception as e:
            import pdb; pdb.set_trace()
