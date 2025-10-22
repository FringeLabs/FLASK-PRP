# Copyright (C) 2025-present by FringeLabs@Github, < https://github.com/FringeLabs >.
#
# This file is part of < https://github.com/FringeLabs/FLASK-PRP > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/FringeLabs/FLASK-PRP/blob/main/LICENSE >
#
# All rights reserved.

import re
import yaml
import csv
from .basic_utils import *
import os
import json
from openpyxl import Workbook
from collections import Counter
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from datetime import datetime


class TextParser:

    def __init__(
        self, text: str, save_folder: str = r"output/", college_code: str = "NSS"
    ):
        self.text = text
        self._init = None
        self.yaml_path = "src/utils/file_utils/regex.yaml"
        self.regex_data = {}
        self.college_code = college_code
        self.d_time = datetime.now()
        self.GRADE_ORDER = ["S", "A+", "A", "B+", "B", "C+", "C", "D", "P", "Absent", "F"]
        self.save_folder = save_folder
        self.exam_centre = None
        self.exam_name = None
        self.init

    @property
    def init(self):
        if not self._init:
            with open(self.yaml_path, encoding="utf-8") as fr:
                self.regex_data = yaml.safe_load(fr)
            self.format_match_check()
        self._init = True
        return self._init

    def format_match_check(self) -> None:
        c = re.search(self.regex_data["exam_centre_pattern"], self.text)
        e = re.search(self.regex_data["btech_exam_pattern"], self.text)
        if not c:
            raise ValueError("Exam Centre pattern not found")
        if not e:
            raise ValueError("B.Tech Exam pattern not found")
        if not self.college_code:
            matches = re.findall(self.regex_data['college_code_pattern'], self.text)
            if not matches:
                raise ValueError("College code could not be predicted from text")
            most_common = Counter(matches).most_common(1)[0][0]
            self.college_code = most_common
        self.exam_centre, self.exam_name = c.group(1), e.group(1)

    def text_matcher(self):
        n_data = load_subjects("src/utils/file_utils/supported_streams.yaml")
        result = {}
        result_num_data = {}

        for stream_code, subject_name in n_data.items():
            pattern = re.compile(
                rf"({self.college_code}"
                + r"\d{2}"
                + stream_code
                + self.regex_data["student_id_pattern"],
                re.MULTILINE,
            )
            course_grade_pattern = re.compile(self.regex_data["course_code_pattern"])
            result[stream_code] = {}
            result_num_data[stream_code] = {
                "appeared": 0,
                "passed": 0,
                "subjects": {},
                "grade_count": {},
            }

            for match in pattern.finditer(self.text):
                student_id = match.group(1)
                subjects_str = match.group(2)
                subjects = dict(course_grade_pattern.findall(subjects_str))
                result_num_data[stream_code]["appeared"] += 1
                if all(grade not in ["F", "Absent"] for grade in subjects.values()):
                    result_num_data[stream_code]["passed"] += 1
                for scode, grade in subjects.items():
                    result_num_data[stream_code]["grade_count"][grade] = (
                        result_num_data[stream_code]["grade_count"].get(grade, 0) + 1
                    )

                    if scode not in result_num_data[stream_code]["subjects"]:
                        result_num_data[stream_code]["subjects"][scode] = {
                            "appeared": 0,
                            "passed": 0,
                        }

                    result_num_data[stream_code]["subjects"][scode]["appeared"] += 1
                    if grade not in ["F", "AB"]:
                        result_num_data[stream_code]["subjects"][scode]["passed"] += 1

                    grade_key = f"no_of_{grade}_grades"
                    result_num_data[stream_code]["subjects"][scode][grade_key] = (
                        result_num_data[stream_code]["subjects"][scode].get(
                            grade_key, 0
                        )
                        + 1
                    )

                subjects["Arrear Subjects Count"] = sum(
                    1 for grade in subjects.values() if grade in ["F", "Absent"]
                )
                subjects["Arrear Subject Codes"] = ", ".join(
                    [code for code, grade in subjects.items() if grade in ["Absent", "F"]]
                )
                result[stream_code][student_id] = subjects

        return result, result_num_data

    def parse_data_as_json_file(self):
        result = self.text_matcher()
        save_folder = self.__make_dir_if_not_exists()
        json_file_path = os.path.join(save_folder, "results.json")
        with open(json_file_path, "w", encoding="utf-8") as jfile:
            json.dump(result, jfile, indent=4)
        return json_file_path

    def __make_dir_if_not_exists(self):
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        return self.save_folder

    def extract_data_and_return_as_csv(self):
        result, rnd = self.text_matcher()
        exam_centre, exam_name = self.exam_centre, self.exam_name
        save_folder = self.__make_dir_if_not_exists()
        for stream_code, students in result.items():
            xlsx_file_path = os.path.join(save_folder, rf"{stream_code}_results.xlsx")
            wb = Workbook()
            ws = wb.active
            ws.append([f"Exam Centre: {exam_centre}"])
            ws.append([f"Exam Name: {exam_name}"])
            for row in [ws.max_row - 1, ws.max_row]:  
                cell = ws.cell(row=row, column=1)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")
            ws.append([])
            ws.append(
            [
                f"Stream: {stream_code} - "
                f"{load_subjects('src/utils/file_utils/supported_streams.yaml')[stream_code]} "
                f"(Generated on: {self.d_time.strftime('%Y-%m-%d %H:%M:%S')})"
            ]
        )
            for i in range(1, 2):
                cell = ws.cell(row=ws.max_row, column=i)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")
            ws.append([])

            fieldnames = ["Student ID"] + list(next(iter(students.values()), {}).keys())
            ws.append(fieldnames)
            for col in range(1, len(fieldnames) + 1):
                cell = ws.cell(row=ws.max_row, column=col)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="e60000", end_color="e60000", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")

            for student_id, subjects in students.items():
                row = [student_id] + [subjects.get(sub, "") for sub in fieldnames[1:]]
                ws.append(row)
                for col in range(2, len(row) + 1):
                    ws.cell(row=ws.max_row, column=col).alignment = Alignment(horizontal="center")

            ws.append([])
            total_appeared = rnd[stream_code]["appeared"]
            total_passed = rnd[stream_code]["passed"]
            pass_percent = (total_passed / total_appeared * 100) if total_appeared > 0 else 0

            summary_rows = [
    ["=== Overall Summary ==="],
    [f"Total Students Appeared: {total_appeared}"],
    [f"Total Students Passed: {total_passed}"],
    [f"Overall Pass Percentage: {pass_percent:.2f}%"]
]

            for row_data in summary_rows:
                ws.append(row_data)
                for col in range(1, len(row_data) + 1):
                    cell = ws.cell(row=ws.max_row, column=col)
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

            ws.append([])

            all_grades = [g for g in self.GRADE_ORDER if g in rnd[stream_code]["grade_count"]]
            ws.append(["GRADE WISE COUNT"])
            for i in range(1, 2):
                cell = ws.cell(row=ws.max_row, column=i)
                cell.font = Font(bold=True)
            ws.append(["Grade"] + all_grades)
            ws.append(["Count"] + [rnd[stream_code]["grade_count"].get(g, 0) for g in all_grades])
            for col in range(1, len(all_grades) + 2):
                cell = ws.cell(row=ws.max_row - 1, column=col)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="e60000", end_color="e60000", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            for row in range(ws.max_row - 1, ws.max_row + 1):
                for col in range(2, len(all_grades) + 2):
                    ws.cell(row=row, column=col).alignment = Alignment(horizontal="center")

            ws.append([])
            ws.append(["SUBJECT WISE PERFORMANCE STATISTICS"])
            for i in range(1, 2):
                cell = ws.cell(row=ws.max_row, column=i)
                cell.font = Font(bold=True, color="000000")
                cell.alignment = Alignment(horizontal="left")
            subject_table_headers = ["Subject Code", "Appeared", "Passed", "Pass %"] + all_grades
            ws.append(subject_table_headers)
            for col in range(1, len(subject_table_headers) + 1):
                cell = ws.cell(row=ws.max_row, column=col)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="e60000", end_color="e60000", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")

            for subject_code, stats in rnd[stream_code]["subjects"].items():
                pass_percentage = (stats["passed"] / stats["appeared"] * 100) if stats["appeared"] > 0 else 0
                row = [subject_code, stats["appeared"], stats["passed"], f"{pass_percentage:.2f}"]
                for grade in all_grades:
                    grade_key = f"no_of_{grade}_grades"
                    row.append(stats.get(grade_key, 0))
                ws.append(row)
                for col in range(2, len(row) + 1):
                    ws.cell(row=ws.max_row, column=col).alignment = Alignment(horizontal="center")

            for col in range(1, ws.max_column + 1):
                max_length = 0
                for cell in ws[get_column_letter(col)]:
                    try:
                        max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                ws.column_dimensions[get_column_letter(col)].width = max_length + 2

            wb.save(xlsx_file_path)
        return save_folder
