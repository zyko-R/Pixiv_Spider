import threading
from Process.Interface import *


class Adapter:
    def __init__(self, file_name, id_list):
        self.file_name, self.id_list = file_name, id_list
        self.process_id()

    class Download(threading.Thread):
        def __init__(self, file_name, id_list):
            super().__init__()
            self.file_name, self.id_list = file_name, id_list

    class DownloadIMG(Download):
        def run(self):
            asyncio.set_event_loop(asyncio.new_event_loop())
            result = ProcLauncher(PackageIMG(self.id_list)).Result
            ProcLauncher(WriteIMG(self.file_name, result))

    class DownloadGIF(Download):
        def run(self):
            asyncio.set_event_loop(asyncio.new_event_loop())
            result = ProcLauncher(PackageGIF(self.id_list)).Result
            ProcLauncher(WriteGIF(self.file_name, result))

    def process_id(self):
        r18_file_name = f'[R18]{self.file_name}'
        nor_file_name = f'[NOR]{self.file_name}'
        ids_nor, ids_r18 = ProcLauncher(MiddlePackage(self.id_list)).Result
        task_list = [
            self.DownloadIMG(nor_file_name, ids_nor['img']),
            self.DownloadIMG(r18_file_name, ids_r18['img']),
            self.DownloadGIF(nor_file_name, ids_nor['gif']),
            self.DownloadGIF(r18_file_name, ids_r18['gif'])
        ]
        for task in task_list:
            task.start()
        for task in task_list:
            task.join()


class Crawler(ABC):
    @abstractmethod
    def crawl(self):
        pass


class Prototype(Crawler):
    file_name, id_list = None, None

    def __init__(self):
        self.r18_file_name = f'[R18]{self.file_name}'
        self.nor_file_name = f'[NOR]{self.file_name}'

    def crawl(self):
        Adapter(self.file_name, self.id_list)
        self.end()

    def end(self):
        if os.path.exists(f'./{self.r18_file_name}'):
            Zip(f'./{self.r18_file_name}').zip()
            shutil.rmtree(f'./{self.r18_file_name}')
        if os.path.exists(f'./{self.nor_file_name}'):
            Zip(f'./{self.nor_file_name}').zip()
            shutil.rmtree(f'./{self.nor_file_name}')


