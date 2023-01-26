from PixivCrawler.Crawler.SemiCrawler.HandlerCell.HandlerType import *
from PixivCrawler.Crawler.SemiCrawler.HandlerCell.HandlerAPI import *

from PixivCrawler.Util.Requests.Proxy import Download
from PixivCrawler.Util.ThreadManager import ThreadLauncher, Wait


class ICrawler(ABC):
    @abstractmethod
    def crawl(self):
        pass


class IDHandler(ICrawler):
    file_name, id_list = None, None
    __unique_instance = None

    def __new__(cls):
        if not hasattr(cls, '__unique_instance'):
            orig = super(ICrawler, cls)
            cls.__unique_instance = orig.__new__(cls)
        return cls.__unique_instance

    def crawl(self):
        url_list = [f'https://www.pixiv.net/artworks/{_id}' for _id in self.id_list]
        html_list = Download.response(url_list)['html']
        img, gif = FilterForm(self.id_list, html_list).filter()
        task_list = [Filter(FilterType(img['ids'], img['html'])), Filter(FilterType(gif['ids'], gif['html']))]
        result = ThreadLauncher(Wait(task_list))
        nor_img, r18_img = result[0] if isinstance(result[0], tuple) else (None, None)
        nor_gif, r18_gif = result[1] if isinstance(result[1], tuple) else (None, None)

        ids = {'IMG': [], 'GIF': []}
        for img_ids, gif_ids in zip([nor_img, r18_img], [nor_gif, r18_gif]):
            if isinstance(img_ids, dict) and 'ids' in img_ids:
                ids['IMG'].append(img_ids['ids'])
            if isinstance(gif_ids, dict) and 'ids' in img_ids:
                ids['GIF'].append(gif_ids['ids'])

        api = {'Parse': [ParseIMG, ParseGIF], 'Store': [StoreIMG, StoreGIF]}
        for p_api, s_api, key in zip(api['Parse'], api['Store'], ids.keys()):
            task_list = [Parse(p_api(param)) for param in ids[key]]
            infos = ThreadLauncher(Wait(task_list))
            task_list = [Store(s_api(f'{pre}{self.file_name}', infos))
                         for pre, infos in zip(['[NOR]', '[R18]'], infos)]
            ThreadLauncher(Wait(task_list))

        task_list = [Store(ZIPFile(f'[NOR]{self.file_name}')), Store(ZIPFile(f'[R18]{self.file_name}'))]
        ThreadLauncher(Wait(task_list))




