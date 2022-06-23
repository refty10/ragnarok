import sys
import os
import re
import json
from color_print import ColorPrint
from glob import glob
from dir_maker import DirMaker
from issue_checker import IssueChecker
from database import Database

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


class Ragnarok:
    def __init__(self, settings_filename="", mkdir_flag=True):
        self.make_dir = mkdir_flag
        settings_filename = settings_filename if settings_filename != "" else self.setting_selector()
        setting_filepath = f"{CURRENT_DIR}/settings/{settings_filename}"
        # setting_filepath = f"{CURRENT_DIR}/settings/subject_08_practice.json"
        self.settings = json.load(open(setting_filepath, encoding="utf-8"))
        self.db = Database()
        self.dir_path = self.settings["dir_path"]
        self.subject = self.settings["subject"]
        self.issues = self.settings["issues"]
        self.db.insert_subject(**self.subject)
        for issue in self.issues:
            self.db.insert_issue(
                issue["id"], issue["title"], self.subject["id"])
        if mkdir_flag and (not DirMaker.run(self.dir_path)):
            sys.exit()

    def setting_selector(self):
        settings_path = f"{CURRENT_DIR}/settings/"
        settings = []

        for setting in glob(f"{settings_path}*.json"):
            settings.append(setting[len(settings_path):])
            print(setting[len(settings_path):])

        while True:
            print("> > Please Select Setting", end=" : ")
            select = input()
            if select in settings:
                return select
            ColorPrint.magenta("Not Exist Setting")

    def run(self):
        # 提出一覧取得
        dirs = glob(CURRENT_DIR + "/temp/**")
        if mkdir_flag:
            # 未提出者の割り出し
            unsubmitted_students = self.get_unsubmitted_student(dirs)
            # 未提出を登録
            self.insert_unsubmitted_student(unsubmitted_students)
        # 提出者の登録
        for dir in dirs:
            # 学籍番号
            student_id = dir[-6:]
            # 提出ファイル一覧
            submits = glob(dir + "/*.c")
            # 採点処理
            print(f'========== {student_id} ==========')
            self.single_check(student_id, submits)

    def get_unsubmitted_student(self, dirs):
        submitted_students = []
        for dir in dirs:
            # 学籍番号
            submitted_students.append(dir[-6:])
        print(len(submitted_students))
        return self.db.find_student_on_unspecified(submitted_students)

    def insert_unsubmitted_student(self, students):
        for student_id in students:
            print(f'========== {student_id} ==========')
            for issue in self.issues:
                # Resultプリセット
                submit_result = {
                    "id": f'{student_id}_{self.subject["id"]}_{issue["id"]}',
                    "result": False,
                    "status_code": "NOT_SUBMITTED",
                    "output": "",
                    "subject_id": self.subject["id"],
                    "issue_id": issue["id"],
                    "student_id": student_id
                }
                self.show_submit_result(submit_result)
                self.db.insert_submit(**submit_result)
                self.db.commit()

    def single_check(self, student_id, submits):
        #　採点設定の読み込み
        for issue in self.issues:
            # Resultプリセット
            submit_result = {
                "id": f'{student_id}_{self.subject["id"]}_{issue["id"]}',
                "result": True,
                "status_code": "OK",
                "output": "",
                "subject_id": self.subject["id"],
                "issue_id": issue["id"],
                "student_id": student_id
            }
            # 対象のファイルパスを取得
            filepath = self.get_submit_filepath(
                issue["filename_regex"], submits)
            # 該当のファイルが見つからない
            if filepath is None:
                submit_result = {
                    **submit_result,
                    "status_code": "CAN_NOT_FIND_SOURCECODE",
                    "result": False,
                }
            # 提出者
            else:
                # コンパイルするファイルを表示
                print(filepath)
                result = IssueChecker.run(filepath, issue["check_code"])
                submit_result = {
                    **submit_result,
                    **result,
                }
            self.show_submit_result(submit_result)
            self.db.insert_submit(**submit_result)
            self.db.commit()

    def get_submit_filepath(self, regex, submits):
        temp = [s for s in submits if re.match(regex, s)]
        if not len(temp) > 0:
            return None
        return temp[0]

    def show_submit_result(self, submit_result):
        print('>>', end=" ")
        ColorPrint.cyan(f'{submit_result["id"]}')
        if submit_result["result"]:
            ColorPrint.green(f'● : {submit_result["status_code"]}')
        else:
            ColorPrint.magenta(f'● : {submit_result["status_code"]}')

        if submit_result["status_code"] != "CAN_NOT_COMPILE":
            ColorPrint.yellow(submit_result["output"][:1000])
        else:
            ColorPrint.red(submit_result["output"][:1000])

        print()


settings_filename = ""
mkdir_flag = True
for arg in sys.argv:
    if arg[-5:] == ".json":
        settings_filename = arg
    elif arg == "--skip":
        mkdir_flag = False

ragnarok = Ragnarok(settings_filename, mkdir_flag)
ragnarok.run()
