from Spider.Prototype import *
from Spider.plugins import *


class CrawlerMixin(ABC):
    @staticmethod
    def clone_crawler():
        return Crawler


class FocusedAuthorCrawler(CrawlerMixin):
    def __init__(self):
        plugin = ParametricPackage(ExceptAuthorID())
        self.clone_crawler()(plugin).work()


class AuthorTraceCrawler(CrawlerMixin):
    def __init__(self):
        plugin = NonparametricPackage(ExceptAuthorTrace())
        self.clone_crawler()(plugin).work()


class SubArtworkCrawler(CrawlerMixin):
    def __init__(self):
        plugin = NonparametricPackage(ExceptAuthorSub())
        self.clone_crawler()(plugin).work()


class RankingCrawler(CrawlerMixin):
    def __init__(self):
        plugin = NonparametricPackage(ExceptRanking())
        self.clone_crawler()(plugin).work()
