from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Schedule(models.Model):
    _name = "university.schedule"
    _description = "Class Schedule"
    _rec_name = "code"
    _order = "day_of_week,start_time"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    code = fields.Char(
        string="Schedule Code",
        readonly=True,
        copy=False,
        default="New",
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

    day_of_week = fields.Selection(
        [
            ("mon", "Monday"),
            ("tue", "Tuesday"),
            ("wed", "Wednesday"),
            ("thu", "Thursday"),
            ("fri", "Friday"),
            ("sat", "Saturday"),
            ("sun", "Sunday"),
        ],
        string="Day",
        required=True,
    )

    start_time = fields.Float(
        string="Start Time",
        required=True,
    )

    end_time = fields.Float(
        string="End Time",
        required=True,
    )

    room = fields.Char(
        string="Room",
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
            self.room = self.classroom_id.room

    # =====================================================
    # CREATE
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            if vals.get("code", "New") == "New":

                vals["code"] = (
                    self.env["ir.sequence"]
                    .next_by_code("university.schedule")
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

                vals["room"] = classroom.room

        return super().create(vals_list)

    # =====================================================
    # CONSTRAINT
    # =====================================================

    @api.constrains(
        "start_time",
        "end_time",
    )
    def _check_time(self):

        for rec in self:

            if rec.start_time >= rec.end_time:

                raise ValidationError(
                    "End time must be greater than start time."
                )

    @api.constrains(
        "teacher_id",
        "day_of_week",
        "start_time",
        "end_time",
    )
    def _check_duplicate(self):

        for rec in self:

            duplicate = self.search([
                ("teacher_id", "=", rec.teacher_id.id),
                ("day_of_week", "=", rec.day_of_week),
                ("id", "!=", rec.id),
            ])

            if duplicate:

                raise ValidationError(
                    "Teacher already has a schedule on this day."
                )