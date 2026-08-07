from odoo import api, fields, models


class Classroom(models.Model):
    _name = "university.classroom"
    _description = "Classroom"
    _rec_name = "name"
    _order = "code"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    code = fields.Char(
        string="Classroom Code",
        copy=False,
        readonly=True,
        default="New",
    )

    name = fields.Char(
        string="Classroom Name",
        required=True,
    )

    subject_id = fields.Many2one(
        "university.subject",
        string="Subject",
        required=True,
    )

    teacher_id = fields.Many2one(
        "university.teacher",
        string="Teacher",
        required=True,
    )

    room = fields.Char(
        string="Room",
    )

    semester = fields.Selection(
        [
            ("hk1", "Semester 1"),
            ("hk2", "Semester 2"),
            ("summer", "Summer"),
        ],
        string="Semester",
        default="hk1",
    )

    year = fields.Integer(
        string="School Year",
        default=lambda self: fields.Date.today().year,
    )

    max_student = fields.Integer(
        string="Maximum Students",
        default=40,
    )

    note = fields.Text(
        string="Note",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # =====================================================
    # RELATION
    # =====================================================

    student_ids = fields.One2many(
        "university.student",
        "classroom_id",
        string="Students",
    )

    enrollment_ids = fields.One2many(
        "university.enrollment",
        "classroom_id",
        string="Enrollments",
    )

    grade_ids = fields.One2many(
        "university.grade",
        "classroom_id",
        string="Grades",
    )

    attendance_ids = fields.One2many(
        "university.attendance",
        "classroom_id",
        string="Attendance",
    )

    schedule_ids = fields.One2many(
        "university.schedule",
        "classroom_id",
        string="Schedules",
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    student_count = fields.Integer(
        compute="_compute_count",
    )

    enrollment_count = fields.Integer(
        compute="_compute_count",
    )

    grade_count = fields.Integer(
        compute="_compute_count",
    )

    attendance_count = fields.Integer(
        compute="_compute_count",
    )

    schedule_count = fields.Integer(
        compute="_compute_count",
    )

    # =====================================================
    # COMPUTE
    # =====================================================

    @api.depends(
        "student_ids",
        "enrollment_ids",
        "grade_ids",
        "attendance_ids",
        "schedule_ids",
    )
    def _compute_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)
            rec.enrollment_count = len(rec.enrollment_ids)
            rec.grade_count = len(rec.grade_ids)
            rec.attendance_count = len(rec.attendance_ids)
            rec.schedule_count = len(rec.schedule_ids)

    # =====================================================
    # SQL CONSTRAINT
    # =====================================================

    _sql_constraints = [
        (
            "classroom_code_unique",
            "unique(code)",
            "Classroom code already exists!",
        ),
    ]

    # =====================================================
    # CREATE
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "New") == "New":
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code(
                        "university.classroom"
                    )
                    or "New"
                )
        return super().create(vals_list)

    # =====================================================
    # SMART BUTTON
    # =====================================================

    def action_students(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Students",
            "res_model": "university.student",
            "view_mode": "list,form",
            "domain": [("classroom_id", "=", self.id)],
        }

    def action_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Enrollments",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("classroom_id", "=", self.id)],
        }

    def action_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Grades",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("classroom_id", "=", self.id)],
        }

    def action_attendance(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Attendance",
            "res_model": "university.attendance",
            "view_mode": "list,form",
            "domain": [("classroom_id", "=", self.id)],
        }

    def action_schedules(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Schedules",
            "res_model": "university.schedule",
            "view_mode": "list,form",
            "domain": [("classroom_id", "=", self.id)],
        }
