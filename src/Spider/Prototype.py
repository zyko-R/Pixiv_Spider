from ProcessID.Parser import *
from ProcessID.Pipeline import *


class Prototype:
    def __init__(self, plugin_package):
        file_name, self.id_list = plugin_package.run()
        self.r18_file_name = f'[R18]{file_name}'
        self.nor_file_name = f'[NOR]{file_name}'
        self.run()
        self.end()

    def end(self):
        if os.path.exists(f'./{self.r18_file_name}'):
            Zip(self.r18_file_name, Zip.zip)
            shutil.rmtree(f'./{self.r18_file_name}')
        if os.path.exists(f'./{self.nor_file_name}'):
            Zip(self.nor_file_name, Zip.zip)
            shutil.rmtree(f'./{self.nor_file_name}')

    def run(self):
        ids_nor, ids_r18 = MiddleCaller(self.id_list, MiddlePackage()).Result
        result = PackageCaller(ids_nor['img'], PackageIMG()).Result
        WriteCaller(result, self.nor_file_name, WriteIMG())
        result = PackageCaller(ids_r18['img'], PackageIMG()).Result
        WriteCaller(result, self.r18_file_name, WriteIMG())
        result = PackageCaller(ids_nor['gif'], PackageGIF()).Result
        WriteCaller(result, self.nor_file_name, WriteGIF())
        result = PackageCaller(ids_r18['gif'], PackageGIF()).Result
        WriteCaller(result, self.r18_file_name, WriteGIF())
