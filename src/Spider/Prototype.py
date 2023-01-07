from IDProcess.Parser import *
from IDProcess.Pipeline import *


class Crawler:
    def __init__(self, id_list, _author_info):
        self.author_info = _author_info
        self.id_list = id_list
        self.author_id = None
        self.r18_file_name = None
        self.nor_file_name = None

    def work(self):
        self.start()
        self.middle()
        self.end()

    def start(self):
        if re.match("^[0-9]*$", self.author_info) is not None:
            author_name = SecondINFOCaller(self.author_info, SecondINFOAuthorName()).Result
            self.author_id = self.author_info
        else:
            self.author_id = SecondINFOCaller(self.author_info, SecondINFOAuthorID()).Result
            author_name = self.author_info

        self.r18_file_name = f'[R18]{author_name}'
        self.nor_file_name = f'[NOR]{author_name}'

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

