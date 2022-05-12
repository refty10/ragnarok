import pandas as pd
import os
from database import Database

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def run():
    # Read CSV
    filepath = f"{CURRENT_DIR}/data/students.csv"
    csv = pd.read_csv(filepath_or_buffer=filepath, encoding="UTF-8", sep=",")
    # Connect database
    db = Database()
    # Create tables
    db.create_table_students()
    db.create_table_subjects()
    db.create_table_issues()
    db.create_table_submits()
    db.create_table_ratings()
    # Insert students
    for student in csv[["学籍番号", "学生氏名"]].values:
        student[0] = student[0].lower()
        student[1] = student[1].replace("　", " ")
        db.insert_student(student[0], student[1].replace("　", " "))
    # Commit
    db.commit()
    db.close()


def test_insert():
    db = Database()
    db.insert_subject("02_01", "第二回 演習問題課題")
    db.insert_issue("02_issue2", "02_issue2_K21000.c", "02_01")
    db.insert_submit(True, "OK", "#####", "02_01", "02_issue2", "k21002")
    db.insert_scores(75, "02_01", "k21002")
    db.commit()
    db.close()


run()
# test_insert()
