from PixivCrawler.CrawlerCaller import CrawlCaller, Executor, By


def colorstr(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class Client:
    class CommandPlugins:
        def __init__(self, caller: CrawlCaller):
            self.Caller = caller

        @staticmethod
        def key():
            while True:
                try:
                    return int(input(colorstr(f'>? ', form=1, code=31)))
                except ValueError:
                    print(colorstr('Type in an Integer', form=1, code=31))
                    continue

        def start_crawling(self):
            self.Caller.Executor.action()
            self.Caller.Executor.CrawlerList.clear()

        def undo_crawl(self):
            crawler_list = self.Caller.Executor.CrawlerList
            if len(crawler_list) == 0:
                print(colorstr(f'CommandList VOID', form=1, code=31))
            else:
                print(colorstr(f'Undo <{type(crawler_list[-1]).__name__}>', form=1, code=31))
                self.Caller.undo()

        def register(self, scheme: By):
            self.Caller.enable(scheme)

    def __init__(self):
        self.scheme_list = [
            ('Artworks by Similar *Artwork*', By.Artwork),
            ('Artworks by *Author*', By.AuthorID),
            ('Artworks by *Following*', By.Following),
            ('Artworks by *Ranking* ', By.Ranking),
        ]
        self.menu_str = f"  TYPE\n" + \
                        f"   0 | {colorstr('StartCrawling', form=1, code=32)}\n" + \
                        f"  -1 | {colorstr('Undo', form=1, code=31)}\n"

        for index, scheme in enumerate(self.scheme_list):
            self.menu_str += f'\n   {index + 1} | {colorstr(scheme[0], form=1, code=33)}'

        while True:
            try:
                global_src_limit = int(input(colorstr('global source limit = ', form=1, code=31)))
                if global_src_limit < 0:
                    raise ValueError
                break
            except ValueError:
                print(colorstr('Type in a positive integer', form=1, code=31))
        self.Caller = self.CommandPlugins(CrawlCaller(Executor(global_src_limit)))

    def run(self):
        print(self.menu_str)
        while True:
            key = self.Caller.key()
            match key:
                case key if 0 < key <= len(self.scheme_list): self.Caller.register(self.scheme_list[key - 1][1])
                case 0: self.Caller.start_crawling()
                case -1: self.Caller.undo_crawl()
                case _: print(colorstr(f'Unknown Command', form=1, code=31))

