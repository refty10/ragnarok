from glob import glob
from zipfile import ZipFile
import shutil
import os
import sys
from color_print import ColorPrint
import pathlib

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


class DirMaker:
    @classmethod
    def run(self, dirname):
        os.makedirs('temp', exist_ok=True)
        shutil.rmtree('temp')
        os.makedirs('temp', exist_ok=True)
        if not self.download_check(dirname):
            return False
        self.scoring_dir_maker(dirname)
        return True

    @classmethod
    def download_check(self, dirname):
        # pass_len = len(dir)
        flag = True
        blank_dir = []

        dirs = glob(dirname + "/**")
        for dir in dirs:
            files = glob(dir + "/*")
            if not len(files) > 0:
                flag = False
                blank_dir.append(dir)

        if not flag:
            ColorPrint.magenta("!!!!  WARNING FIND BLANK DIR !!!!")
            for dir in blank_dir:
                print(f'>> {dir}')

        return flag

    @classmethod
    def scoring_dir_maker(self, dirname):
        pass_len = len(dirname)
        files = glob(dirname + "/**/*.*", recursive=True)
        for file in files:
            # 学籍番号の取得
            id = file[pass_len + 1:pass_len + 7]
            ColorPrint.cyan(id)
            print(file)

            if (not os.path.isdir(file)) and ".c" == file[-2:]:
                filename = os.path.basename(file)
                os.makedirs(f'temp/{id}', exist_ok=True)
                shutil.copyfile(file, f'temp/{id}/{filename}')

            elif (not os.path.isdir(file)) and ".zip" == file[-4:]:
                with ZipFile(file) as existing_zip:
                    existing_zip.extractall(f'temp/{id}')
                    self.zip_dir_checker(id)

    @classmethod
    def zip_dir_checker(self, id):
        files = glob(f"{CURRENT_DIR}/temp/{id}/**/*", recursive=True)
        for file in files:
            user_dir = f"{CURRENT_DIR}/temp/{id}"
            # main.c対策
            if (not os.path.isdir(file)) and "main.c" == file[-6:]:
                dirname = os.path.dirname(file)

                replaced_file = file.replace("/", " ")
                replaced_file = replaced_file.replace("\\", " ")
                split_dirs = replaced_file.split(" ")

                if split_dirs[-2] != id:
                    filename = f"{split_dirs[-2]}.c"
                    oldpath = pathlib.Path(file)
                    oldpath.rename(pathlib.Path(os.path.join(user_dir, f"{dirname}/{filename}")))
                    # 再帰処理
                    return self.zip_dir_checker(id)

                # ディレクトリ名に.cつけるやつの対処
            if os.path.isdir(file) and ".c" == file[-2:]:
                oldpath = pathlib.Path(file)
                oldpath.rename(pathlib.Path(file[:-2]))
                # 再帰処理
                return self.zip_dir_checker(id)

            if (not os.path.isdir(file)) and ".c" == file[-2:]:
                filename = os.path.basename(file)
                verification_dir = os.path.join(user_dir, filename)
                if verification_dir != file:
                    shutil.copyfile(file, f'{user_dir}/{filename}')


def main():
    dir = os.path.join(CURRENT_DIR, sys.argv[1])
    if os.path.isdir(dir):
        DirMaker.run(dir)


if __name__ == "__main__":
    main()
