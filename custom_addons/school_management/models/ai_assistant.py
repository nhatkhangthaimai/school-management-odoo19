import json
import urllib.request
import urllib.error

from odoo import api, fields, models


class SchoolAIAssistant(models.Model):
    _name = "school.ai.assistant"
    _description = "School AI Assistant"
    _order = "create_date desc"

    name = fields.Char(
        string="Name",
        default="AI Assistant",
        required=True,
    )

    question = fields.Text(
        string="Question",
        required=True,
    )

    ai_answer = fields.Text(
        string="AI Answer",
        readonly=True,
    )

    # =========================================================
    # CONFIG
    # =========================================================

    @api.model
    def _get_ai_config(self):
        ICP = self.env["ir.config_parameter"].sudo()

        api_key = ICP.get_param(
            "school_management.openrouter_api_key"
        )

        if not api_key:
            api_key = ICP.get_param(
                "school_management.openai_api_key"
            )

        model = ICP.get_param(
            "school_management.openrouter_model"
        )

        if not model:
            model = ICP.get_param(
                "school_management.openai_model"
            )

        if not model:
            model = "openai/gpt-4o-mini"

        return api_key, model

    # =========================================================
    # HELPER
    # =========================================================

    def _safe_value(
        self,
        record,
        field_name,
        default="",
    ):
        if not record:
            return default

        if field_name not in record._fields:
            return default

        value = getattr(
            record,
            field_name,
            False,
        )

        if value is False or value is None:
            return default

        if hasattr(value, "display_name"):
            return value.display_name

        return value

    # =========================================================
    # FIND STUDENT
    # =========================================================

    def _find_student(self, question):

        Student = self.env[
            "university.student"
        ].sudo()

        question_text = (
            question or ""
        ).strip().lower()

        if not question_text:
            return Student.browse()

        students = Student.search([])

        found_students = Student.browse()

        for student in students:

            possible_values = []

            if "name" in Student._fields:

                name = getattr(
                    student,
                    "name",
                    False,
                )

                if name:
                    possible_values.append(
                        str(name)
                        .strip()
                        .lower()
                    )

            for field_name in [
                "code",
                "student_code",
                "student_id",
                "roll_number",
            ]:

                if field_name not in Student._fields:
                    continue

                value = getattr(
                    student,
                    field_name,
                    False,
                )

                if value:

                    possible_values.append(
                        str(value)
                        .strip()
                        .lower()
                    )

            for value in possible_values:

                if (
                    value
                    and value in question_text
                ):

                    found_students |= student
                    break

        return found_students

    # =========================================================
    # FIND CLASSROOM
    # =========================================================

    def _find_classroom(self, question):

        Classroom = self.env[
            "university.classroom"
        ].sudo()

        question_text = (
            question or ""
        ).strip().lower()

        if not question_text:
            return Classroom.browse()

        classrooms = Classroom.search([])

        found_classrooms = Classroom.browse()

        for classroom in classrooms:

            possible_values = []

            for field_name in [
                "name",
                "code",
                "class_code",
                "classroom_code",
            ]:

                if field_name not in Classroom._fields:
                    continue

                value = getattr(
                    classroom,
                    field_name,
                    False,
                )

                if value:

                    possible_values.append(
                        str(value)
                        .strip()
                        .lower()
                    )

            for value in possible_values:

                if (
                    value
                    and value in question_text
                ):

                    found_classrooms |= classroom
                    break

        return found_classrooms

    # =========================================================
    # STUDENT DETAIL
    # =========================================================

    def _get_student_context(
        self,
        students,
    ):

        Grade = self.env[
            "university.grade"
        ].sudo()

        result = []

        for student in students:

            student_data = {
                "id": student.id,

                "name": self._safe_value(
                    student,
                    "name",
                    student.display_name,
                ),
            }

            # -------------------------------------------------
            # THÔNG TIN SINH VIÊN
            # -------------------------------------------------

            for field_name in [
                "code",
                "student_code",
                "student_id",
                "email",
                "phone",
                "classroom_id",
                "department_id",
            ]:

                if field_name not in student._fields:
                    continue

                value = getattr(
                    student,
                    field_name,
                    False,
                )

                if value:

                    if hasattr(
                        value,
                        "display_name",
                    ):

                        value = (
                            value.display_name
                        )

                    student_data[
                        field_name
                    ] = value

            # -------------------------------------------------
            # ĐIỂM
            # -------------------------------------------------

            grades = Grade.search([
                (
                    "student_id",
                    "=",
                    student.id,
                ),
            ])

            grade_list = []

            scores = []

            for grade in grades:

                total = grade.total

                if total is not None:

                    try:

                        total = float(total)

                        if (
                            0 <= total <= 10
                        ):

                            scores.append(
                                total
                            )

                    except (
                        ValueError,
                        TypeError,
                    ):

                        total = None

                grade_data = {

                    "grade_code":
                        grade.code,

                    "subject": (
                        grade.subject_id.display_name
                        if grade.subject_id
                        else ""
                    ),

                    "teacher": (
                        grade.teacher_id.display_name
                        if grade.teacher_id
                        else ""
                    ),

                    "semester":
                        grade.semester,

                    "year":
                        grade.year,

                    "attendance":
                        grade.attendance,

                    "midterm":
                        grade.midterm,

                    "final":
                        grade.final,

                    "total":
                        total,

                    "letter_grade":
                        grade.letter_grade,

                    "classification":
                        grade.classification,

                    "status":
                        grade.status,
                }

                grade_list.append(
                    grade_data
                )

            student_data[
                "grades"
            ] = grade_list

            student_data[
                "grade_count"
            ] = len(grade_list)

            # -------------------------------------------------
            # PHÂN TÍCH
            # -------------------------------------------------

            if scores:

                average = round(
                    sum(scores)
                    / len(scores),
                    2,
                )

                student_data[
                    "average_score"
                ] = average

                student_data[
                    "highest_score"
                ] = max(scores)

                student_data[
                    "lowest_score"
                ] = min(scores)

                student_data[
                    "failed_subjects"
                ] = sum(
                    1
                    for score in scores
                    if score < 5
                )

                student_data[
                    "excellent_subjects"
                ] = sum(
                    1
                    for score in scores
                    if score >= 9
                )

                student_data[
                    "good_subjects"
                ] = sum(
                    1
                    for score in scores
                    if 8 <= score < 9
                )

                student_data[
                    "average_subjects"
                ] = sum(
                    1
                    for score in scores
                    if 5 <= score < 8
                )

                if average >= 8.5:

                    student_data[
                        "overall_classification"
                    ] = "Xuất sắc"

                elif average >= 8:

                    student_data[
                        "overall_classification"
                    ] = "Khá"

                elif average >= 6.5:

                    student_data[
                        "overall_classification"
                    ] = (
                        "Khá/Trung bình khá"
                    )

                elif average >= 5:

                    student_data[
                        "overall_classification"
                    ] = "Trung bình"

                else:

                    student_data[
                        "overall_classification"
                    ] = "Yếu"

            else:

                student_data[
                    "average_score"
                ] = None

                student_data[
                    "highest_score"
                ] = None

                student_data[
                    "lowest_score"
                ] = None

                student_data[
                    "failed_subjects"
                ] = 0

                student_data[
                    "excellent_subjects"
                ] = 0

                student_data[
                    "good_subjects"
                ] = 0

                student_data[
                    "average_subjects"
                ] = 0

                student_data[
                    "overall_classification"
                ] = (
                    "Chưa có dữ liệu điểm"
                )

            result.append(
                student_data
            )

        return result

    # =========================================================
    # CLASSROOM DETAIL
    # =========================================================

    def _get_classroom_context(
        self,
        classrooms,
    ):

        Student = self.env[
            "university.student"
        ].sudo()

        Grade = self.env[
            "university.grade"
        ].sudo()

        result = []

        for classroom in classrooms:

            students = Student.search([
                (
                    "classroom_id",
                    "=",
                    classroom.id,
                ),
            ])

            student_list = []

            all_scores = []

            for student in students:

                grades = Grade.search([
                    (
                        "student_id",
                        "=",
                        student.id,
                    ),
                    (
                        "classroom_id",
                        "=",
                        classroom.id,
                    ),
                ])

                scores = []

                for grade in grades:

                    try:

                        score = float(
                            grade.total
                        )

                        if (
                            0 <= score <= 10
                        ):

                            scores.append(
                                score
                            )

                            all_scores.append(
                                score
                            )

                    except (
                        ValueError,
                        TypeError,
                    ):

                        continue

                average = None

                if scores:

                    average = round(
                        sum(scores)
                        / len(scores),
                        2,
                    )

                failed_subjects = sum(
                    1
                    for score in scores
                    if score < 5
                )

                student_list.append({

                    "student_id":
                        student.id,

                    "student_name":
                        student.display_name,

                    "average_score":
                        average,

                    "grade_count":
                        len(scores),

                    "failed_subjects":
                        failed_subjects,
                })

            # -------------------------------------------------
            # ĐIỂM TRUNG BÌNH LỚP
            # -------------------------------------------------

            class_average = None

            if all_scores:

                class_average = round(
                    sum(all_scores)
                    / len(all_scores),
                    2,
                )

            # -------------------------------------------------
            # PHÂN LOẠI SINH VIÊN
            # -------------------------------------------------

            excellent_students = sum(
                1
                for student
                in student_list
                if (
                    student[
                        "average_score"
                    ] is not None
                    and student[
                        "average_score"
                    ] >= 8.5
                )
            )

            good_students = sum(
                1
                for student
                in student_list
                if (
                    student[
                        "average_score"
                    ] is not None
                    and 8 <= student[
                        "average_score"
                    ] < 8.5
                )
            )

            average_students = sum(
                1
                for student
                in student_list
                if (
                    student[
                        "average_score"
                    ] is not None
                    and 5 <= student[
                        "average_score"
                    ] < 8
                )
            )

            weak_students = sum(
                1
                for student
                in student_list
                if (
                    student[
                        "average_score"
                    ] is not None
                    and student[
                        "average_score"
                    ] < 5
                )
            )

            # -------------------------------------------------
            # SINH VIÊN CẦN CHÚ Ý
            # -------------------------------------------------

            warning_students = []

            for student in student_list:

                if (
                    student[
                        "average_score"
                    ] is not None
                    and (
                        student[
                            "average_score"
                        ] < 5
                        or student[
                            "failed_subjects"
                        ] > 0
                    )
                ):

                    warning_students.append(
                        student
                    )

            result.append({

                "classroom_id":
                    classroom.id,

                "classroom_name":
                    classroom.display_name,

                "student_count":
                    len(students),

                "class_average":
                    class_average,

                "excellent_students":
                    excellent_students,

                "good_students":
                    good_students,

                "average_students":
                    average_students,

                "weak_students":
                    weak_students,

                "warning_students":
                    warning_students,

                "students":
                    student_list,
            })

        return result

    # =========================================================
    # SCHOOL CONTEXT
    # =========================================================

    def _get_school_context(self):

        Student = self.env[
            "university.student"
        ].sudo()

        Teacher = self.env[
            "university.teacher"
        ].sudo()

        Department = self.env[
            "university.department"
        ].sudo()

        Subject = self.env[
            "university.subject"
        ].sudo()

        Classroom = self.env[
            "university.classroom"
        ].sudo()

        Enrollment = self.env[
            "university.enrollment"
        ].sudo()

        Grade = self.env[
            "university.grade"
        ].sudo()

        Attendance = self.env[
            "university.attendance"
        ].sudo()

        Schedule = self.env[
            "university.schedule"
        ].sudo()

        # -----------------------------------------------------
        # THỐNG KÊ
        # -----------------------------------------------------

        context = {

            "students":
                Student.search_count([]),

            "teachers":
                Teacher.search_count([]),

            "departments":
                Department.search_count([]),

            "subjects":
                Subject.search_count([]),

            "classrooms":
                Classroom.search_count([]),

            "enrollments":
                Enrollment.search_count([]),

            "grades":
                Grade.search_count([]),

            "attendance_records":
                Attendance.search_count([]),

            "schedules":
                Schedule.search_count([]),
        }

        # -----------------------------------------------------
        # KHOA
        # -----------------------------------------------------

        departments = Department.search([])

        context[
            "department_names"
        ] = [
            department.display_name
            for department in departments
        ]

        # -----------------------------------------------------
        # PHÂN TÍCH ĐIỂM TOÀN TRƯỜNG
        # -----------------------------------------------------

        grades = Grade.search([])

        scores = []

        for grade in grades:

            try:

                score = float(
                    grade.total
                )

                if 0 <= score <= 10:

                    scores.append(
                        score
                    )

            except (
                ValueError,
                TypeError,
            ):

                continue

        if scores:

            context[
                "score_count"
            ] = len(scores)

            context[
                "average_score"
            ] = round(
                sum(scores)
                / len(scores),
                2,
            )

            context[
                "highest_score"
            ] = max(scores)

            context[
                "lowest_score"
            ] = min(scores)

            context[
                "excellent"
            ] = sum(
                1
                for x in scores
                if x >= 8.5
            )

            context[
                "good"
            ] = sum(
                1
                for x in scores
                if 8 <= x < 8.5
            )

            context[
                "fair"
            ] = sum(
                1
                for x in scores
                if 6.5 <= x < 8
            )

            context[
                "average"
            ] = sum(
                1
                for x in scores
                if 5 <= x < 6.5
            )

            context[
                "weak"
            ] = sum(
                1
                for x in scores
                if x < 5
            )

        else:

            context[
                "score_count"
            ] = 0

            context[
                "average_score"
            ] = None

            context[
                "highest_score"
            ] = None

            context[
                "lowest_score"
            ] = None

            context[
                "excellent"
            ] = 0

            context[
                "good"
            ] = 0

            context[
                "fair"
            ] = 0

            context[
                "average"
            ] = 0

            context[
                "weak"
            ] = 0

        # -----------------------------------------------------
        # SINH VIÊN CẦN QUAN TÂM
        # -----------------------------------------------------

        students = Student.search([])

        warning_students = []

        for student in students:

            student_grades = grades.filtered(
                lambda g:
                    g.student_id.id
                    == student.id
            )

            student_scores = []

            for grade in student_grades:

                try:

                    score = float(
                        grade.total
                    )

                    if (
                        0 <= score <= 10
                    ):

                        student_scores.append(
                            score
                        )

                except (
                    ValueError,
                    TypeError,
                ):

                    continue

            if not student_scores:
                continue

            average = (
                sum(student_scores)
                / len(student_scores)
            )

            failed = sum(
                1
                for score
                in student_scores
                if score < 5
            )

            if (
                average < 5
                or failed > 0
            ):

                warning_students.append({

                    "student_id":
                        student.id,

                    "student_name":
                        student.display_name,

                    "average_score":
                        round(
                            average,
                            2,
                        ),

                    "failed_subjects":
                        failed,
                })

        context[
            "warning_students"
        ] = warning_students

        return context

    # =========================================================
    # CALL OPENROUTER
    # =========================================================

    def _call_ai(
        self,
        question,
        context,
        student_context=None,
        classroom_context=None,
    ):

        api_key, model = (
            self._get_ai_config()
        )

        if not api_key:

            return (
                "Chưa cấu hình OpenRouter API Key.\n\n"
                "Vào Cài đặt → AI Assistant "
                "và nhập API Key."
            )

        # =====================================================
        # SYSTEM PROMPT
        # =====================================================

        system_prompt = """
Bạn là AI Assistant của hệ thống quản lý trường học.

QUY TẮC:

1. Trả lời bằng tiếng Việt.

2. Với các câu hỏi liên quan đến trường học,
   điểm số, sinh viên, giáo viên, khoa, môn học,
   lớp học, lịch học, điểm danh:
   CHỈ được sử dụng dữ liệu Odoo được cung cấp.

3. Không được tự bịa số liệu.

4. Không được tự tạo tên sinh viên,
   tên giáo viên, khoa, lớp hoặc môn học.

5. Nếu dữ liệu không có hoặc không đủ,
   phải nói rõ:
   "Chưa có đủ dữ liệu trong hệ thống."

6. Khi người dùng hỏi về một sinh viên cụ thể,
   ưu tiên sử dụng dữ liệu sinh viên được cung cấp.

7. Khi người dùng hỏi về một lớp cụ thể,
   ưu tiên sử dụng dữ liệu lớp được cung cấp.

8. Có thể phân tích, so sánh và đưa ra nhận xét
   dựa trên dữ liệu thực tế.

9. Có thể đưa ra cảnh báo học tập dựa trên dữ liệu.

10. Không được thay đổi dữ liệu trong Odoo.

11. Không tiết lộ API key hoặc thông tin bảo mật.

12. Nếu câu hỏi không liên quan đến hệ thống trường học,
    có thể trả lời kiến thức chung ở mức phù hợp,
    nhưng không được giả vờ rằng thông tin đó
    đến từ cơ sở dữ liệu Odoo.

13. Khi nói về số liệu của hệ thống,
    phải ưu tiên dữ liệu Odoo hơn kiến thức chung.

PHÂN LOẠI ĐIỂM:

- >= 8.5: Xuất sắc
- >= 8.0: Khá
- >= 6.5: Khá/Trung bình khá
- >= 5.0: Trung bình
- < 5.0: Yếu

KHI PHÂN TÍCH SINH VIÊN:

- Điểm trung bình
- Điểm cao nhất
- Điểm thấp nhất
- Số môn đã có điểm
- Số môn dưới 5
- Xếp loại
- Môn cần chú ý nếu có

KHI PHÂN TÍCH LỚP:

- Tên lớp
- Sĩ số
- Điểm trung bình
- Số sinh viên xuất sắc
- Số sinh viên khá
- Số sinh viên trung bình
- Số sinh viên yếu
- Sinh viên cần chú ý
- Nhận xét tổng quan

Nếu lớp có sinh viên có điểm dưới 5,
hãy cảnh báo rõ ràng.

Không được tự suy đoán số liệu
không có trong dữ liệu Odoo.
"""

        # =====================================================
        # USER PROMPT
        # =====================================================

        user_prompt = f"""
DỮ LIỆU TỔNG QUAN CỦA HỆ THỐNG ODOO:

{json.dumps(
    context,
    ensure_ascii=False,
    indent=2,
    default=str,
)}
"""

        # -----------------------------------------------------
        # STUDENT DATA
        # -----------------------------------------------------

        if student_context:

            user_prompt += f"""

DỮ LIỆU SINH VIÊN ĐƯỢC TÌM THẤY:

{json.dumps(
    student_context,
    ensure_ascii=False,
    indent=2,
    default=str,
)}
"""

        # -----------------------------------------------------
        # CLASSROOM DATA
        # -----------------------------------------------------

        if classroom_context:

            user_prompt += f"""

DỮ LIỆU LỚP ĐƯỢC TÌM THẤY:

{json.dumps(
    classroom_context,
    ensure_ascii=False,
    indent=2,
    default=str,
)}
"""

        user_prompt += f"""

CÂU HỎI CỦA NGƯỜI DÙNG:

{question}

Hãy trả lời câu hỏi dựa trên dữ liệu được cung cấp.
"""

        # =====================================================
        # PAYLOAD
        # =====================================================

        payload = {

            "model":
                model,

            "messages": [

                {
                    "role":
                        "system",

                    "content":
                        system_prompt,
                },

                {
                    "role":
                        "user",

                    "content":
                        user_prompt,
                },
            ],

            "max_tokens":
                1500,

            "temperature":
                0.2,
        }

        data = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        # =====================================================
        # OPENROUTER REQUEST
        # =====================================================

        request = urllib.request.Request(

            "https://openrouter.ai/api/v1/chat/completions",

            data=data,

            headers={

                "Content-Type":
                    "application/json",

                "Authorization":
                    f"Bearer {api_key}",

                "HTTP-Referer":
                    "http://localhost:8069",

                "X-Title":
                    "School Management AI Assistant",
            },

            method="POST",
        )

        # =====================================================
        # CALL API
        # =====================================================

        try:

            with urllib.request.urlopen(
                request,
                timeout=60,
            ) as response:

                response_data = json.loads(
                    response
                    .read()
                    .decode("utf-8")
                )

            choices = response_data.get(
                "choices",
                [],
            )

            if not choices:

                return (
                    "AI không trả về kết quả."
                )

            message = choices[0].get(
                "message",
                {},
            )

            answer = message.get(
                "content",
                "",
            )

            if answer:

                return answer.strip()

            return (
                "AI không trả về nội dung."
            )

        # =====================================================
        # HTTP ERROR
        # =====================================================

        except urllib.error.HTTPError as error:

            try:

                error_body = (
                    error.read()
                    .decode("utf-8")
                )

            except Exception:

                error_body = str(error)

            if error.code == 401:

                return (
                    "OpenRouter API Key không hợp lệ.\n\n"
                    "Hãy kiểm tra lại API Key trong "
                    "Cài đặt → AI Assistant."
                )

            if error.code == 402:

                return (
                    "OpenRouter không đủ credit cho model "
                    f"'{model}'.\n\n"
                    "Hãy chọn model rẻ hơn hoặc nạp thêm "
                    "credit trong OpenRouter."
                )

            if error.code == 429:

                return (
                    "OpenRouter đang giới hạn yêu cầu "
                    "hoặc tài khoản đã vượt quota."
                )

            return (
                f"Lỗi OpenRouter API "
                f"({error.code}):\n"
                f"{error_body}"
            )

        # =====================================================
        # CONNECTION ERROR
        # =====================================================

        except urllib.error.URLError as error:

            return (
                "Không thể kết nối OpenRouter.\n\n"
                f"Chi tiết: {error.reason}"
            )

        # =====================================================
        # OTHER ERROR
        # =====================================================

        except Exception as error:

            return (
                "Đã xảy ra lỗi khi gọi AI.\n\n"
                f"Chi tiết: {str(error)}"
            )

    # =========================================================
    # ASK AI
    # =========================================================

    def action_ask_ai(self):

        self.ensure_one()

        if not self.question:

            self.ai_answer = (
                "Vui lòng nhập câu hỏi."
            )

            return True

        # -----------------------------------------------------
        # DỮ LIỆU TOÀN TRƯỜNG
        # -----------------------------------------------------

        context = (
            self._get_school_context()
        )

        # -----------------------------------------------------
        # TÌM SINH VIÊN
        # -----------------------------------------------------

        students = (
            self._find_student(
                self.question
            )
        )

        student_context = None

        if students:

            student_context = (
                self._get_student_context(
                    students
                )
            )

        # -----------------------------------------------------
        # TÌM LỚP
        # -----------------------------------------------------

        classrooms = (
            self._find_classroom(
                self.question
            )
        )

        classroom_context = None

        if classrooms:

            classroom_context = (
                self._get_classroom_context(
                    classrooms
                )
            )

        # -----------------------------------------------------
        # GỌI AI
        # -----------------------------------------------------

        self.ai_answer = (
            self._call_ai(
                self.question,
                context,
                student_context,
                classroom_context,
            )
        )

        return True

    # =========================================================
    # CREATE
    # =========================================================

    @api.model_create_multi
    def create(
        self,
        vals_list,
    ):

        records = super().create(
            vals_list
        )

        for record in records:

            if not record.question:
                continue

            context = (
                record._get_school_context()
            )

            # -----------------------------------------------
            # SINH VIÊN
            # -----------------------------------------------

            students = (
                record._find_student(
                    record.question
                )
            )

            student_context = None

            if students:

                student_context = (
                    record._get_student_context(
                        students
                    )
                )

            # -----------------------------------------------
            # LỚP
            # -----------------------------------------------

            classrooms = (
                record._find_classroom(
                    record.question
                )
            )

            classroom_context = None

            if classrooms:

                classroom_context = (
                    record._get_classroom_context(
                        classrooms
                    )
                )

            # -----------------------------------------------
            # AI
            # -----------------------------------------------

            record.ai_answer = (
                record._call_ai(
                    record.question,
                    context,
                    student_context,
                    classroom_context,
                )
            )

        return records