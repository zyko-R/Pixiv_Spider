from Spider.Prototype import *
from Except.Primary import *


class CrawlerMixin:
    pass


class ByAuthorIDCrawler(CrawlerMixin):
    def __init__(self):
        plugin = PluginPackage(ByAuthorID)
        Prototype(plugin)


class ByArtworkIDCrawler(CrawlerMixin):
    def __init__(self):
        plugin = PluginPackage(ByArtworkID)
        Prototype(plugin)


class ByTraceCrawler(CrawlerMixin):
    def __init__(self):
        plugin = PluginPackage(ByTrace)
        Prototype(plugin)


class BySubCrawler(CrawlerMixin):
    def __init__(self):
        plugin = PluginPackage(BySub)
        Prototype(plugin)


class ByRankingCrawler(CrawlerMixin):
    def __init__(self):
        plugin = PluginPackage(ByRanking)
        Prototype(plugin)
