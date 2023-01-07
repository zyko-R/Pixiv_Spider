from Spider.Prototype import *
from Spider.plugins import *


class CrawlerMixin(ABC):
    @staticmethod
    def clone_crawler():
        return Crawler


class FocusedAuthorCrawler(CrawlerMixin):
    @classmethod
    def process(cls, param, _source_limit):
        id_list = ExceptCaller(param, _source_limit, ExceptAuthor_ID()).Result['id_list']
        cls.clone_crawler()(id_list, param).work()


class IncrementalAuthorCrawler(CrawlerMixin):
    @classmethod
    def process(cls, _source_limit):
        author_id_list = AuthorSub().except_id(_source_limit)
        for author_id in author_id_list:
            cls.clone_crawler()(author_id['id_list'], author_id['author_id']).work()

