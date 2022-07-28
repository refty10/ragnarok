from database import Database
from color_print import ColorPrint
from glob import glob
import os
import sys
import json
import math

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def calculate_rating(settings_filename):
    settings_filename = settings_filename if settings_filename != "" else setting_selector()
    setting_filepath = f"{CURRENT_DIR}/settings/{settings_filename}"
    settings = json.load(open(setting_filepath, encoding="utf-8"))

    # 初期化
    subject_id = settings["subject"]["id"]
    issue_count = len(settings["issues"])
    required_issue_count = settings["required_issue_count"]

    db = Database()
    student_ids = db.find_student_ids()

    for student_id in student_ids:
        submits = db.find_submits_by_subject_and_students(
            subject_id,
            student_id
        )

        base_point = 0
        for submit in submits:
            # Status_Codeによる加点
            if submit[1]:
                base_point += 1
            elif submit[2] == "WRONG_OUTPUT" or submit[2] == "INFINITE_LOOP":
                base_point += 0.5
            elif submit[2] == "WRONG_CODE" or submit[2] == "CAN_NOT_COMPILE":
                base_point += 0.25
            elif submit[2] == "DIRECT_OUTPUT":
                base_point += 0

        # 基本点数計算
        base_rating = base_point / required_issue_count * 100

        rating = 0
        # 加点分の計算(最大点数+25)
        if base_rating > 100:
            max_rating = issue_count / required_issue_count * 100
            additional_point_ratio = 25 / (max_rating - 100)
            additional_point = additional_point_ratio * (base_rating - 100)
            rating = math.ceil(100 + additional_point)
        # 加点がない場合
        else:
            rating = math.ceil(base_rating)

        print(f"{student_id}: ", end="")
        if rating > 99:
            ColorPrint.green(str(rating).rjust(3, ' '), end="")
        elif rating == 0:
            ColorPrint.red(str(rating).rjust(3, ' '), end="")
        else:
            ColorPrint.white(str(rating).rjust(3, ' '), end="")
        print(f" -- {str(base_point).ljust(3, ' ')}")

        db.insert_rating(
            f"{student_id}_{subject_id}", rating, subject_id, student_id
        )

    db.commit()


def setting_selector():
    settings_path = f"{CURRENT_DIR}/settings/"
    settings = []

    for setting in glob(f"{settings_path}*.json"):
        settings.append(setting[len(settings_path):])

    for setting in sorted(settings):
        print(setting)

    while True:
        print("> > Please Select Setting", end=" : ")
        select = input()
        if select in settings:
            return select
        ColorPrint.magenta("Not Exist Setting")


settings_filename = ""
if len(sys.argv) > 1:
    settings_filename = sys.argv[1]
calculate_rating(settings_filename)
