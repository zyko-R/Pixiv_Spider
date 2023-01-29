from PixivCrawler.Crawler.Plugins import *


class By:
    AuthorID = ByAuthorID
    Artwork = ByArtworkID
    Following = ByFollowing
    Ranking = ByRanking


class Executor:
    def __init__(self, src_limit): IDPlugin.src_limit, self.CrawlerList = src_limit, []

    def action(self): [crawler.crawl() for crawler in self.CrawlerList]


class CrawlCaller:
    __Prototype = IDHandler()
    
    def __init__(self, executor: Executor): self.Executor = executor

    def enable(self, plugin): self.Executor.CrawlerList.append(plugin(self.__Prototype))

    def undo(self):
        if len(self.Executor.CrawlerList) != 0:
            self.Executor.CrawlerList.pop(-1)


            
