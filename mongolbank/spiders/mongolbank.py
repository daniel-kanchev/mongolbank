import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from mongolbank.items import Article


class mongolbankSpider(scrapy.Spider):
    name = 'mongolbank'
    start_urls = ['https://www.mongolbank.mn/eng/news.aspx?tid=1']

    def parse(self, response):
        links = response.xpath('//table[@class="uk-table"]//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="text-grey uk-text-bold text-12 "]/text()').get()
        if date:
            date = " ".join(date.split()[1:])

        content = response.xpath('//div[@class="uk-width-large-3-4 uk-width-medium-2-3 uk-width-1-1"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[5:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
