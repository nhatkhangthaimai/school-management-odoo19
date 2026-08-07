from odoo import api, fields, models


class Subject(models.Model):
    _name = "university.subject"
    _description = "Subject"
    _rec_name = "name"
    _order = "code"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    code = fields.Char(
        string="Subject Code",
        copy=False,
        readonly=True,
        default="New",
    )

    name = fields.Char(
        string="Subject Name",
        required=True,
    )

    department_id = fields.Many2one(
        "university.department",
        string="Department",
        required=True,
    )

    teacher_id = fields.Many2one(
        "university.teacher",
        string="Teacher",
        required=True,
    )

    credit = fields.Integer(
        string="Credits",
        default=3,
    )

    theory_hours = fields.Integer(
        string="Theory Hours",
        default=30,
    )

    practice_hours = fields.Integer(
        string="Practice Hours",
        default=15,
    )

    description = fields.Text(
        string="Description",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # =====================================================
    # RELATION
    # =====================================================

    classroom_ids = fields.One2many(
        "university.classroom",
        "subject_id",
        string="Classrooms",
    )

    grade_ids = fields.One2many(
        "university.grade",
        "subject_id",
        string="Grades",
    )

    schedule_ids = fields.One2many(
        "university.schedule",
        "subject_id",
        string="Schedules",
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    classroom_count = fields.Integer(
        compute="_compute_count",
    )

    grade_count = fields.Integer(
        compute="_compute_count",
    )

    schedule_count = fields.Integer(
        compute="_compute_count",
    )

    student_count = fields.Integer(
        compute="_compute_count",
    )

    # =====================================================
    # COMPUTE
    # =====================================================

    @api.depends(
        "classroom_ids",
        "grade_ids",
        "schedule_ids",
    )
    def _compute_count(self):
        for rec in self:

            rec.classroom_count = len(rec.classroom_ids)

            rec.grade_count = len(rec.grade_ids)

            rec.schedule_count = len(rec.schedule_ids)

            rec.student_count = sum(
                len(cls.student_ids)
                for cls in rec.classroom_ids
            )

    # =====================================================
    # SQL CONSTRAINT
    # =====================================================

    _sql_constraints = [
        (
            "subject_code_unique",
            "unique(code)",
            "Subject code already exists!",
        ),
        (
            "subject_name_unique",
            "unique(name)",
            "Subject name already exists!",
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
                        "university.subject"
                    )
                    or "New"
                )

        return super().create(vals_list)

    # =====================================================
    # SMART BUTTON
    # =====================================================

    def action_classrooms(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Classrooms",
            "res_model": "university.classroom",
            "view_mode": "list,form",
            "domain": [("subject_id", "=", self.id)],
        }

    def action_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Grades",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("subject_id", "=", self.id)],
        }

    def action_schedules(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Schedules",
            "res_model": "university.schedule",
            "view_mode": "list,form",
            "domain": [("subject_id", "=", self.id)],
        }
