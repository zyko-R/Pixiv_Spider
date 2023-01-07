from Spider.Prototype import *
from Spider.plugins import *


class CrawlerMixin(ABC):
    @staticmethod
    def clone_crawler():
        return Crawler


class FocusedAuthorCrawler(CrawlerMixin):
    def __init__(self, param, _source_limit):
        id_list = FocusedExceptCaller(param, _source_limit, ExceptAuthorID()).Result['id_list']
        self.clone_crawler()(id_list, param).work()


class IncrementalAuthorCrawler(CrawlerMixin):
    def __init__(self, _source_limit):
        author_id_list = IncrementExceptCaller(_source_limit, ExceptAuthorSub()).Result
        for author_id in author_id_list:
            self.clone_crawler()(author_id['id_list'], author_id['author_id']).work()

