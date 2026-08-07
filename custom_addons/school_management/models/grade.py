from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Grade(models.Model):
    _name = "university.grade"
    _description = "Student Grade"
    _rec_name = "code"
    _order = "id desc"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    code = fields.Char(
        string="Grade Code",
        readonly=True,
        copy=False,
        default="New",
    )

    student_id = fields.Many2one(
        "university.student",
        string="Student",
        required=True,
        ondelete="cascade",
    )

    classroom_id = fields.Many2one(
        "university.classroom",
        string="Classroom",
        required=True,
        ondelete="cascade",
    )

    subject_id = fields.Many2one(
        "university.subject",
        string="Subject",
        readonly=True,
        store=True,
    )

    teacher_id = fields.Many2one(
        "university.teacher",
        string="Teacher",
        readonly=True,
        store=True,
    )

    semester = fields.Selection(
        [
            ("hk1", "Semester 1"),
            ("hk2", "Semester 2"),
            ("summer", "Summer"),
        ],
        string="Semester",
        readonly=True,
    )

    year = fields.Integer(
        string="School Year",
        readonly=True,
    )

    attendance = fields.Float(
        string="Attendance",
        digits=(4, 2),
        default=0,
    )

    midterm = fields.Float(
        string="Midterm",
        digits=(4, 2),
        default=0,
    )

    final = fields.Float(
        string="Final",
        digits=(4, 2),
        default=0,
    )

    total = fields.Float(
        string="Total",
        compute="_compute_result",
        store=True,
    )

    letter_grade = fields.Char(
        string="Letter Grade",
        compute="_compute_result",
        store=True,
    )

    classification = fields.Selection(
        [
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("fair", "Fair"),
            ("average", "Average"),
            ("weak", "Weak"),
        ],
        string="Classification",
        compute="_compute_result",
        store=True,
    )

    status = fields.Selection(
        [
            ("pass", "Pass"),
            ("fail", "Fail"),
        ],
        string="Status",
        compute="_compute_result",
        store=True,
    )

    note = fields.Text()

    active = fields.Boolean(
        default=True,
    )

    # =====================================================
    # COMPUTE
    # =====================================================

    @api.depends(
        "attendance",
        "midterm",
        "final",
    )
    def _compute_result(self):

        for rec in self:

            rec.total = round(
                rec.attendance * 0.1 +
                rec.midterm * 0.3 +
                rec.final * 0.6,
                2,
            )

            if rec.total >= 9:
                rec.letter_grade = "A"
                rec.classification = "excellent"

            elif rec.total >= 8:
                rec.letter_grade = "B"
                rec.classification = "good"

            elif rec.total >= 6.5:
                rec.letter_grade = "C"
                rec.classification = "fair"

            elif rec.total >= 5:
                rec.letter_grade = "D"
                rec.classification = "average"

            else:
                rec.letter_grade = "F"
                rec.classification = "weak"

            rec.status = (
                "pass"
                if rec.total >= 5
                else "fail"
            )

    # =====================================================
    # ONCHANGE
    # =====================================================

    @api.onchange("classroom_id")
    def _onchange_classroom(self):
        if self.classroom_id:
            self.subject_id = self.classroom_id.subject_id.id
            self.teacher_id = self.classroom_id.teacher_id.id
            self.semester = self.classroom_id.semester
            self.year = self.classroom_id.year

    # =====================================================
    # CREATE
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("code", "New") == "New":

                vals["code"] = (
                    self.env["ir.sequence"].next_by_code(
                        "university.grade"
                    )
                    or "New"
                )

            classroom = self.env[
                "university.classroom"
            ].browse(vals.get("classroom_id"))

            if classroom:

                vals["subject_id"] = classroom.subject_id.id

                vals["teacher_id"] = classroom.teacher_id.id

                vals["semester"] = classroom.semester

                vals["year"] = classroom.year

        return super().create(vals_list)

    # =====================================================
    # CONSTRAINT
    # =====================================================

    @api.constrains(
        "attendance",
        "midterm",
        "final",
    )
    def _check_score(self):

        for rec in self:

            for score in (
                rec.attendance,
                rec.midterm,
                rec.final,
            ):

                if score < 0 or score > 10:
                    raise ValidationError(
                        "Score must be between 0 and 10."
                    )

    @api.constrains(
        "student_id",
        "classroom_id",
    )
    def _check_duplicate(self):

        for rec in self:

            duplicate = self.search([
                ("student_id", "=", rec.student_id.id),
                ("classroom_id", "=", rec.classroom_id.id),
                ("id", "!=", rec.id),
            ])

            if duplicate:
                raise ValidationError(
                    "Grade already exists."
                )

    # =====================================================
    # BUTTON
    # =====================================================

    def action_calculate(self):

        self._compute_result()

        return True