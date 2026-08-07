from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Attendance(models.Model):
    _name = "university.attendance"
    _description = "Attendance"
    _rec_name = "code"
    _order = "date desc"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    code = fields.Char(
        string="Attendance Code",
        copy=False,
        readonly=True,
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

    date = fields.Date(
        string="Date",
        default=fields.Date.context_today,
        required=True,
    )

    status = fields.Selection(
        [
            ("present", "Present"),
            ("late", "Late"),
            ("absent", "Absent"),
            ("leave", "Leave"),
        ],
        string="Status",
        default="present",
        required=True,
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

    # =====================================================
    # CREATE
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("code", "New") == "New":

                vals["code"] = (
                    self.env["ir.sequence"]
                    .next_by_code("university.attendance")
                    or "New"
                )

            classroom = self.env[
                "university.classroom"
            ].browse(vals.get("classroom_id"))

            if classroom:

                vals["subject_id"] = classroom.subject_id.id

                vals["teacher_id"] = classroom.teacher_id.id

        return super().create(vals_list)

    # =====================================================
    # CONSTRAINT
    # =====================================================

    @api.constrains(
        "student_id",
        "classroom_id",
        "date",
    )
    def _check_duplicate(self):

        for rec in self:

            duplicate = self.search([
                ("student_id", "=", rec.student_id.id),
                ("classroom_id", "=", rec.classroom_id.id),
                ("date", "=", rec.date),
                ("id", "!=", rec.id),
            ])

            if duplicate:

                raise ValidationError(
                    "Attendance already exists."
                )