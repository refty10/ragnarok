import os
import sqlite3

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


class Database:
    DB_NAME = f"{CURRENT_DIR}/db/ragnarok.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.DB_NAME)
        self.cur = self.conn.cursor()

    def find_student_ids(self):
        sql = "SELECT id FROM students"
        self.execute(sql)
        result = []
        for student in self.fetchall():
            result.append(student[0])
        return result

    def find_submits_by_subject_and_students(self, subject_id, student_id):
        sql = "SELECT * FROM submits\n"
        sql += f'WHERE subject_id="{subject_id}" AND student_id="{student_id}"'
        self.execute(sql)
        return self.fetchall()

    def insert_student(self, id, name):
        if self.exist_student(id):
            self.delete_student(id)
        sql = "INSERT INTO students(id, name)\n"
        sql += f'VALUES("{id}", "{name}")'
        self.execute(sql)

    def find_student_on_unspecified(self, students):
        sql = "SELECT id FROM students\n"
        sql += "WHERE id NOT IN ("
        for student in students:
            sql += f'"{student}",'
        sql = sql[:-1]
        sql += ")"
        self.execute(sql)
        result = []
        for student in self.fetchall():
            result.append(student[0])
        return result

    def exist_student(self, id):
        sql = f'SELECT COUNT(*) FROM students WHERE id = "{id}"'
        self.execute(sql)
        return True if self.fetchall()[0][0] > 0 else False

    def delete_student(self, id):
        sql = f'DELETE FROM students WHERE id = "{id}"'
        self.execute(sql)

    def insert_subject(self, id, title):
        if self.exist_subject(id):
            self.delete_subject(id)
        sql = "INSERT INTO subjects(id, title)\n"
        sql += f'VALUES("{id}", "{title}")'
        self.execute(sql)

    def exist_subject(self, id):
        sql = f'SELECT COUNT(*) FROM subjects WHERE id = "{id}"'
        self.execute(sql)
        return True if self.fetchall()[0][0] > 0 else False

    def delete_subject(self, id):
        sql = f'DELETE FROM subjects WHERE id = "{id}"'
        self.execute(sql)

    def insert_issue(self, id, title, subject_id):
        if self.exist_issue(id):
            self.delete_issue(id)
        sql = "INSERT INTO issues(id, title, subject_id)\n"
        sql += f'VALUES("{id}", "{title}", "{subject_id}")'
        self.execute(sql)

    def exist_issue(self, id):
        sql = f'SELECT COUNT(*) FROM issues WHERE id = "{id}"'
        self.execute(sql)
        return True if self.fetchall()[0][0] > 0 else False

    def delete_issue(self, id):
        sql = f'DELETE FROM issues WHERE id = "{id}"'
        self.execute(sql)

    def insert_submit(self, id, result, status_code, output, subject_id, issue_id, student_id):
        if self.exist_submit(id):
            self.delete_submit(id)
        result = 1 if result else 0

        # SQLインジェクション対策
        output = output.replace('"', "")
        output = output.replace("\0", "")

        sql = "INSERT INTO submits(id, result, status_code, output, subject_id, issue_id, student_id)\n"
        sql += f'VALUES("{id}", {result}, "{status_code}", "{output}", "{subject_id}", "{issue_id}", "{student_id}")'
        self.execute(sql)

    def exist_submit(self, id):
        sql = f'SELECT COUNT(*) FROM submits WHERE id = "{id}"'
        self.execute(sql)
        return True if self.fetchall()[0][0] > 0 else False

    def delete_submit(self, id):
        sql = f'DELETE FROM submits WHERE id = "{id}"'
        self.execute(sql)

    def insert_rating(self, id, rating, subject_id, student_id):
        if self.exist_rating(id):
            self.delete_rating(id)
        sql = "INSERT INTO ratings(id, rating, subject_id, student_id)\n"
        sql += f'VALUES("{id}", {rating}, "{subject_id}", "{student_id}")'
        self.execute(sql)

    def exist_rating(self, id):
        sql = f'SELECT COUNT(*) FROM ratings WHERE id = "{id}"'
        self.execute(sql)
        return True if self.fetchall()[0][0] > 0 else False

    def delete_rating(self, id):
        sql = f'DELETE FROM ratings WHERE id = "{id}"'
        self.execute(sql)

    def create_table_students(self):
        sql = "CREATE TABLE\n"
        sql += "students(id STRING PRIMARY KEY, name STRING)"
        self.execute(sql)

    def create_table_subjects(self):
        sql = "CREATE TABLE\n"
        sql += "subjects(id STRING PRIMARY KEY, title STRING)"
        self.execute(sql)

    def create_table_issues(self):
        sql = "CREATE TABLE\n"
        sql += "issues(id STRING PRIMARY KEY, title STRING, subject_id STRING)"
        self.execute(sql)

    def create_table_submits(self):
        sql = "CREATE TABLE\n"
        sql += "submits(id STRING PRIMARY KEY, result BOOLEAN, status_code STRING, output STRING, subject_id STRING, issue_id STRING, student_id STRING)"
        self.execute(sql)

    def create_table_ratings(self):
        sql = "CREATE TABLE\n"
        sql += "ratings(id STRING PRIMARY KEY, rating INTEGER, subject_id STRING, student_id STRING)"
        self.execute(sql)

    def fetchall(self):
        return self.cur.fetchall()

    def execute(self, sql):
        self.cur.execute(sql)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.commit()
        self.conn.close()
