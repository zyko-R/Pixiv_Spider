from PixivCrawler.CrawlerCaller import CrawlCaller, Executor, By


def colorstr(message, code, form=0):
    return f'\033[{form};{code}m{message}\033[0m'


class Client:
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
            global_src_limit = input(colorstr('global source limit = ', form=1, code=31))
            if global_src_limit.isdigit() and int(global_src_limit) > 0:
                global_src_limit = int(global_src_limit)
                break
            else:
                print(colorstr('Type in a positive integer', form=1, code=31))
        self.Caller = CrawlCaller(Executor(global_src_limit))
        print(self.menu_str)

    def run(self):
        while True:
            key = input(colorstr(f'>? ', form=1, code=31))
            if key.isdigit() or int(key) < 0:
                key = int(key)
                break
            else:
                print(colorstr('Type in an Integer', form=1, code=31))
        match key:
            case key if 0 < key <= len(self.scheme_list):
                self.Caller.enable(self.scheme_list[key - 1][1])
            case 0:
                self.Caller.Executor.action()
            case -1:
                self.Caller.undo()
            case _:
                print(colorstr(f'Unknown Command', form=1, code=31))
        self.run()


