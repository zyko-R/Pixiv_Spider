from PixivCrawler.Crawler.Plugins import *


class Wrapper:
    @staticmethod
    def display_on_action(func):
        def display(self):
            command_list = [type(c).__name__ for c in self.CrawlerList]
            rep = "', '"
            print(colorstr(f'{str(command_list).replace(rep, "->", len(command_list))}', form=1, code=37))
            func(self)
            self.CrawlerList.clear()
        return display

    @staticmethod
    def display_on_undo(func):
        def display(self):
            crawler_list = self.Executor.CrawlerList
            if len(crawler_list) == 0:
                print(colorstr(f'CommandList VOID', form=1, code=31))
            else:
                print(colorstr(f'Undo <{type(crawler_list[-1]).__name__}>', form=1, code=31))
                func(self)
        return display

    @staticmethod
    def display_on_enable(func):
        def display(self, plugin):
            func(self, plugin)
            print(colorstr(f'<Append {plugin.__name__}>', form=1, code=34))
        return display


class By:
    AuthorID = ByAuthorID
    Artwork = ByArtworkID
    Following = ByFollowing
    Ranking = ByRanking


class Executor:
    def __init__(self, src_limit): IDPlugin.src_limit, self.CrawlerList = src_limit, []

    @Wrapper.display_on_action
    def action(self): [crawler.crawl() for crawler in self.CrawlerList]


class CrawlCaller:
    __Prototype = IDHandler()
    
    def __init__(self, executor: Executor): self.Executor = executor

    @Wrapper.display_on_enable
    def enable(self, plugin): self.Executor.CrawlerList.append(plugin(self.__Prototype))

    @Wrapper.display_on_undo
    def undo(self): self.Executor.CrawlerList.pop(-1) if len(self.Executor.CrawlerList) != 0 else None


