from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Enrollment(models.Model):
    _name = "university.enrollment"
    _description = "Enrollment"
    _rec_name = "code"
    _order = "id desc"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    code = fields.Char(
        string="Enrollment Code",
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

    enroll_date = fields.Date(
        string="Enroll Date",
        default=fields.Date.context_today,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    note = fields.Text(
        string="Note",
    )

    active = fields.Boolean(
        default=True,
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
                vals["code"] = self.env["ir.sequence"].next_by_code(
                    "university.enrollment"
                ) or "New"

            classroom = self.env["university.classroom"].browse(
                vals.get("classroom_id")
            )

            if classroom:
                vals["subject_id"] = classroom.subject_id.id
                vals["teacher_id"] = classroom.teacher_id.id
                vals["semester"] = classroom.semester
                vals["year"] = classroom.year

        return super().create(vals_list)

    # =====================================================
    # CONSTRAINT
    # =====================================================

    @api.constrains("student_id", "classroom_id")
    def _check_duplicate(self):

        for rec in self:

            duplicate = self.search([
                ("student_id", "=", rec.student_id.id),
                ("classroom_id", "=", rec.classroom_id.id),
                ("id", "!=", rec.id),
            ])

            if duplicate:
                raise ValidationError(
                    "Student has already enrolled in this classroom."
                )

    # =====================================================
    # BUTTON
    # =====================================================

    def action_confirm(self):
        self.write({
            "state": "confirmed",
        })

    def action_cancel(self):
        self.write({
            "state": "cancel",
        })

    def action_draft(self):
        self.write({
            "state": "draft",
        })