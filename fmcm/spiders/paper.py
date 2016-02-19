# -*- coding: utf-8 -*-

import codecs

from scrapy import Request
from scrapy.spiders import Spider
from scrapy.selector import Selector

from fmcm.items import FmcmItem


class PaperSpider(Spider):

    name = 'paper'
    allowed_domins = ['thepaper.cn']
    # start_urls = [
    #     'http://www.thepaper.cn',
    #     ajax_url % 2,
    #     ajax_url % 3,
    #     ajax_url % 4,
    # ]
    crawl_page = 0
    news_count = 0
    ajax_url = 'http://www.thepaper.cn/load_chosen.jsp?nodeids=25949&topCids=1432510,1432601,1432305,1432553,&pageidx=%s&lastTime=1455669153242'

    def start_requests(self):
        yield Request('http://www.thepaper.cn', self.parse)
        for i in range(1, 11):
            yield Request(self.ajax_url % i, self.parse)
        # yield Request(self.ajax_url % 2, self.parse)
        # yield Request(self.ajax_url % 3, self.parse)

    def parse(self, response):
        try:
            self.crawl_page += 1

            sel = Selector(response)
            # import pdb; pdb.set_trace()
            name = response.url.split('/')[-2]
            if name:
                file_name = '%s.html' % name
            else:
                file_name = 'home_page.html'
            with open(file_name, 'w') as f:
                f.write(response.body)
            if response.url == 'http://www.thepaper.cn':
                hot_list = sel.xpath('//*[@class="list_hot"][@style!="display:none"]')
                for article_list in hot_list:
                    for article in article_list.xpath('li'):
                        list_detail = {}
                        list_title = article.xpath('a/text()').extract()
                        url = article.xpath('a/attribute::href').extract()
                        # import pdb; pdb.set_trace()
                        if not (list_title and url):
                            continue
                        url = response.urljoin(url[0])
                        self.news_count += 1
                        list_detail['list_title'] = list_title[0]
                        list_detail['url'] = url
                        list_detail['news_count'] = self.news_count
                        f = codecs.open('article_list.txt', 'a', 'utf-8')
                        f.write('%s. ' % self.news_count)
                        f.write(
                            'title: %s\n    url: %s\n' % (list_detail['list_title'], url))
                        f.flush()
                        request = Request(url, callback=self.parse_news_detail)
                        request.meta.update(list_detail)
                        yield request
            else:
                articles = sel.xpath('//*[@class="news_li"]')
                for article in articles:
                    list_detail = {}
                    # import pdb; pdb.set_trace()
                    list_title = article.xpath('h2/a/text()').extract()
                    url = article.xpath('h2/a/attribute::href').extract()
                    if not (url and list_title):
                        continue
                    url = response.urljoin(url[0])
                    self.news_count += 1
                    list_detail['list_title'] = list_title[0]
                    list_detail['url'] = url[0]
                    self.news_count += 1
                    list_detail['news_count'] = self.news_count
                    f = codecs.open('article_list.txt', 'a', 'utf-8')
                    f.write('%s. ' % self.news_count)
                    f.write(
                        'title: %s\n    url: %s\n' % (list_detail['list_title'], url))
                    f.flush()

                    # for news detail process
                    request = Request(url, callback=self.parse_news_detail)
                    request.meta.update(list_detail)
                    yield request
                    # yield Request(self.ajax_url % (self.crawl_page + 1), self.parse)
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
                    (response.meta['news_count'], response.meta['list_title'],
                        response.meta['url'], title, news_editor, zan,
                        news_about, news_keyword, content)
                )
        except Exception as e:
            import pdb; pdb.set_trace()
