from odoo import api, fields, models


class UniversityDashboard(models.Model):
    _name = "university.dashboard"
    _description = "University Dashboard"

    name = fields.Char(
        default="Dashboard",
    )

    total_student = fields.Integer(
        compute="_compute_dashboard",
    )

    total_teacher = fields.Integer(
        compute="_compute_dashboard",
    )

    total_department = fields.Integer(
        compute="_compute_dashboard",
    )

    total_subject = fields.Integer(
        compute="_compute_dashboard",
    )

    total_classroom = fields.Integer(
        compute="_compute_dashboard",
    )

    total_enrollment = fields.Integer(
        compute="_compute_dashboard",
    )

    total_grade = fields.Integer(
        compute="_compute_dashboard",
    )

    total_attendance = fields.Integer(
        compute="_compute_dashboard",
    )

    average_score = fields.Float(
        compute="_compute_dashboard",
    )

    pass_rate = fields.Float(
        compute="_compute_dashboard",
    )

    fail_rate = fields.Float(
        compute="_compute_dashboard",
    )

    @api.depends()
    def _compute_dashboard(self):

        Student = self.env["university.student"]
        Teacher = self.env["university.teacher"]
        Department = self.env["university.department"]
        Subject = self.env["university.subject"]
        Classroom = self.env["university.classroom"]
        Enrollment = self.env["university.enrollment"]
        Grade = self.env["university.grade"]
        Attendance = self.env["university.attendance"]

        grades = Grade.search([])

        for rec in self:

            rec.total_student = Student.search_count([])

            rec.total_teacher = Teacher.search_count([])

            rec.total_department = Department.search_count([])

            rec.total_subject = Subject.search_count([])

            rec.total_classroom = Classroom.search_count([])

            rec.total_enrollment = Enrollment.search_count([])

            rec.total_grade = Grade.search_count([])

            rec.total_attendance = Attendance.search_count([])

            if grades:

                rec.average_score = round(
                    sum(grades.mapped("total")) / len(grades),
                    2,
                )

                passed = len(
                    grades.filtered(
                        lambda g: g.status == "pass"
                    )
                )

                failed = len(
                    grades.filtered(
                        lambda g: g.status == "fail"
                    )
                )

                rec.pass_rate = round(
                    passed * 100 / len(grades),
                    2,
                )

                rec.fail_rate = round(
                    failed * 100 / len(grades),
                    2,
                )

            else:

                rec.average_score = 0

                rec.pass_rate = 0

                rec.fail_rate = 0