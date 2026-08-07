from odoo import api, fields, models


class Teacher(models.Model):
    _name = "university.teacher"
    _description = "Teacher"
    _rec_name = "name"
    _order = "code"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    code = fields.Char(
        string="Teacher Code",
        copy=False,
        readonly=True,
        default="New",
    )

    name = fields.Char(
        string="Teacher Name",
        required=True,
    )

    department_id = fields.Many2one(
        "university.department",
        string="Department",
        required=True,
    )

    phone = fields.Char(
        string="Phone",
    )

    email = fields.Char(
        string="Email",
    )

    degree = fields.Selection(
        [
            ("bachelor", "Bachelor"),
            ("master", "Master"),
            ("doctor", "Doctor"),
        ],
        string="Degree",
        default="master",
    )

    image = fields.Image(
        string="Photo",
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

    subject_ids = fields.One2many(
        "university.subject",
        "teacher_id",
        string="Subjects",
    )

    classroom_ids = fields.One2many(
        "university.classroom",
        "teacher_id",
        string="Classrooms",
    )

    schedule_ids = fields.One2many(
        "university.schedule",
        "teacher_id",
        string="Schedules",
    )

    attendance_ids = fields.One2many(
        "university.attendance",
        "teacher_id",
        string="Attendances",
    )

    grade_ids = fields.One2many(
        "university.grade",
        "teacher_id",
        string="Grades",
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    subject_count = fields.Integer(
        compute="_compute_count",
    )

    classroom_count = fields.Integer(
        compute="_compute_count",
    )

    schedule_count = fields.Integer(
        compute="_compute_count",
    )

    attendance_count = fields.Integer(
        compute="_compute_count",
    )

    grade_count = fields.Integer(
        compute="_compute_count",
    )

    # =====================================================
    # COMPUTE
    # =====================================================

    @api.depends(
        "subject_ids",
        "classroom_ids",
        "schedule_ids",
        "attendance_ids",
        "grade_ids",
    )
    def _compute_count(self):
        for rec in self:
            rec.subject_count = len(rec.subject_ids)
            rec.classroom_count = len(rec.classroom_ids)
            rec.schedule_count = len(rec.schedule_ids)
            rec.attendance_count = len(rec.attendance_ids)
            rec.grade_count = len(rec.grade_ids)

    # =====================================================
    # SQL CONSTRAINT
    # =====================================================

    _sql_constraints = [
        (
            "teacher_code_unique",
            "unique(code)",
            "Teacher code already exists!",
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
                        "university.teacher"
                    )
                    or "New"
                )

        return super().create(vals_list)

    # =====================================================
    # SMART BUTTON
    # =====================================================

    def action_subjects(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Subjects",
            "res_model": "university.subject",
            "view_mode": "list,form",
            "domain": [("teacher_id", "=", self.id)],
        }

    def action_classrooms(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Classrooms",
            "res_model": "university.classroom",
            "view_mode": "list,form",
            "domain": [("teacher_id", "=", self.id)],
        }

    def action_schedules(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Schedules",
            "res_model": "university.schedule",
            "view_mode": "list,form",
            "domain": [("teacher_id", "=", self.id)],
        }

    def action_attendance(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Attendance",
            "res_model": "university.attendance",
            "view_mode": "list,form",
            "domain": [("teacher_id", "=", self.id)],
        }

    def action_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Grades",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("teacher_id", "=", self.id)],
        }
