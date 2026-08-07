from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Department(models.Model):
    _name = "university.department"
    _description = "Department"
    _rec_name = "name"
    _order = "code"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    code = fields.Char(
        string="Department Code",
        required=True,
        copy=False,
        readonly=True,
        default="New",
    )

    name = fields.Char(
        string="Department Name",
        required=True,
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

    teacher_ids = fields.One2many(
        "university.teacher",
        "department_id",
        string="Teachers",
    )

    student_ids = fields.One2many(
        "university.student",
        "department_id",
        string="Students",
    )

    subject_ids = fields.One2many(
        "university.subject",
        "department_id",
        string="Subjects",
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    teacher_count = fields.Integer(
        string="Teachers",
        compute="_compute_count",
        store=False,
    )

    student_count = fields.Integer(
        string="Students",
        compute="_compute_count",
        store=False,
    )

    subject_count = fields.Integer(
        string="Subjects",
        compute="_compute_count",
        store=False,
    )

    # =====================================================
    # COMPUTE
    # =====================================================

    @api.depends(
        "teacher_ids",
        "student_ids",
        "subject_ids",
    )
    def _compute_count(self):
        for rec in self:
            rec.teacher_count = len(rec.teacher_ids)
            rec.student_count = len(rec.student_ids)
            rec.subject_count = len(rec.subject_ids)

    # =====================================================
    # CONSTRAINT
    # =====================================================

    _sql_constraints = [
        (
            "department_code_unique",
            "unique(code)",
            "Department code already exists!",
        ),
        (
            "department_name_unique",
            "unique(name)",
            "Department name already exists!",
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
                        "university.department"
                    )
                    or "New"
                )
        return super().create(vals_list)

    # =====================================================
    # SMART BUTTON
    # =====================================================

    def action_teachers(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Teachers",
            "res_model": "university.teacher",
            "view_mode": "list,form",
            "domain": [("department_id", "=", self.id)],
        }

    def action_students(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Students",
            "res_model": "university.student",
            "view_mode": "list,form",
            "domain": [("department_id", "=", self.id)],
        }

    def action_subjects(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Subjects",
            "res_model": "university.subject",
            "view_mode": "list,form",
            "domain": [("department_id", "=", self.id)],
        }
