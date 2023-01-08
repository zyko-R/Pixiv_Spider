from Spider.Prototype import *
from Spider.plugins import *


class CrawlerMixin(ABC):
    @staticmethod
    def clone_crawler():
        return Crawler

    @staticmethod
    def get_info(author_info):
        if re.match("^[0-9]*$", author_info) is not None:
            author_name = SecondINFOCaller(author_info, SecondINFOAuthorName()).Result
            author_id = author_info
        else:
            author_id = SecondINFOCaller(author_info, SecondINFOAuthorID()).Result
            author_name = author_info
        return author_name, author_id


class FocusedAuthorCrawler(CrawlerMixin):
    def __init__(self, param, _source_limit):
        author_name, author_id = self.get_info(param)
        id_list = FocusedExceptCaller(param, _source_limit, ExceptAuthorID()).Result['id_list']
        self.clone_crawler()(id_list, author_name).work()


class IncrementalAuthorCrawler(CrawlerMixin):
    def __init__(self, _source_limit):
        author_id_list = IncrementExceptCaller(_source_limit, ExceptAuthorSub()).Result
        for author_id in author_id_list:
            author_name, author_id = self.get_info(author_id)
            self.clone_crawler()(author_id['id_list'], author_name).work()


class IncrementalRankingCrawler(CrawlerMixin):
    def __init__(self, _source_limit):
        id_list = IncrementExceptCaller(_source_limit, ExceptRanking()).Result
        self.clone_crawler()(id_list, 'Ranking').work()
