import asyncio
import threading

from ..SemiCrawler.HandlerCell.Implementer import *


class ICrawler(ABC):
    @abstractmethod
    def crawl(self):
        pass


class IDHandler(ICrawler):
    file_name, id_list = None, None
    __unique_instance = None

    def __new__(cls):
        if not hasattr(cls, '__unique_instance'):
            orig = super(IDHandler, cls)
            cls.__unique_instance = orig.__new__(cls)
        return cls.__unique_instance

    def crawl(self):
        r18_file_name = f'[R18]{self.file_name}'
        nor_file_name = f'[NOR]{self.file_name}'
        nor_img, r18_img, nor_gif, r18_gif = DoGroupID(self.id_list).result
        task_list = [
            self.DownloadIMG(nor_file_name, nor_img),
            self.DownloadIMG(r18_file_name, r18_img),
            self.DownloadGIF(nor_file_name, nor_gif),
            self.DownloadGIF(r18_file_name, r18_gif)
        ]
        for task in task_list:
            task.start()
        for task in task_list:
            task.join()
        self.end()

    class Download(threading.Thread):
        def __init__(self, file_name, id_list):
            super().__init__()
            self.file_name, self.id_list = file_name, id_list

    class DownloadIMG(Download):
        def run(self):
            asyncio.set_event_loop(asyncio.new_event_loop())
            result = DoParseIMG(self.id_list).result
            DoStoreIMG(result, self.file_name)

    class DownloadGIF(Download):
        def run(self):
            asyncio.set_event_loop(asyncio.new_event_loop())
            result = DoParseGIF(self.id_list).result
            DoStoreGIF(result, self.file_name)

    def end(self):
        def _zip(file_path):
            print(colour_str(f'Zipping: ', form=1, code=31), end='')
            with zipfile.ZipFile(file_path + '.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                for item in os.listdir(file_path):
                    z.write(file_path + os.sep + item)
            print(colour_str(f'[finish]', form=1, code=32))

        r18_file_name = f'[R18]{self.file_name}'
        nor_file_name = f'[NOR]{self.file_name}'

        if os.path.exists(f'./{r18_file_name}'):
            _zip(f'./{r18_file_name}')
            shutil.rmtree(f'./{r18_file_name}')
        if os.path.exists(f'./{nor_file_name}'):
            _zip(f'./{nor_file_name}')
            shutil.rmtree(f'./{nor_file_name}')
