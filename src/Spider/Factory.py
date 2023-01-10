from Spider.Prototype import *
from Spider.plugins import *


class CrawlerMixin(ABC):
    @staticmethod
    def clone_crawler():
        return Crawler


class ByAuthorIDCrawler(CrawlerMixin):
    def __init__(self):
        plugin = PluginPackage(ByAuthorID())
        self.clone_crawler()(plugin).work()


class ByArtworkIDCrawler(CrawlerMixin):
    def __init__(self):
        plugin = PluginPackage(ByArtworkID())
        self.clone_crawler()(plugin).work()


class ByTraceCrawler(CrawlerMixin):
    def __init__(self):
        plugin = AutoPluginPackage(ByTrace())
        self.clone_crawler()(plugin).work()


class BySubCrawler(CrawlerMixin):
    def __init__(self):
        plugin = AutoPluginPackage(BySub())
        self.clone_crawler()(plugin).work()


class ByRankingCrawler(CrawlerMixin):
    def __init__(self):
        plugin = AutoPluginPackage(ByRanking())
        self.clone_crawler()(plugin).work()
