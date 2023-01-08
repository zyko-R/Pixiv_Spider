from Process.Parser import *
from Process.Pipeline import *


class Crawler:
    def __init__(self, id_list, file_name):
        self.file_name = file_name
        self.id_list = id_list
        self.author_id = None
        self.r18_file_name = None
        self.nor_file_name = None

    def work(self):
        self.start()
        self.middle()
        self.end()

    def start(self):

        self.r18_file_name = f'[R18]{self.file_name}'
        self.nor_file_name = f'[NOR]{self.file_name}'

    def end(self):
        if os.path.exists(f'./{self.r18_file_name}'):
            Pipeline.zip(self.r18_file_name)
            shutil.rmtree(f'./{self.r18_file_name}')
        if os.path.exists(f'./{self.nor_file_name}'):
            Pipeline.zip(self.nor_file_name)
            shutil.rmtree(f'./{self.nor_file_name}')

    def middle(self):
        ids_nor, ids_r18 = MiddleCaller(self.id_list, MiddlePackage()).Result
        result = PackageCaller(ids_nor['img'], PackageIMG()).Result
        WriteCaller(result, self.nor_file_name, WriteIMG())
        result = PackageCaller(ids_r18['img'], PackageIMG()).Result
        WriteCaller(result, self.r18_file_name, WriteIMG())
        result = PackageCaller(ids_nor['gif'], PackageGIF()).Result
        WriteCaller(result, self.nor_file_name, WriteGIF())
        result = PackageCaller(ids_r18['gif'], PackageGIF()).Result
        WriteCaller(result, self.r18_file_name, WriteGIF())

