from odoo import api, fields, models


class Student(models.Model):
    _name = "university.student"
    _description = "Student"
    _rec_name = "name"
    _order = "student_code"

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    student_code = fields.Char(
        string="Student Code",
        copy=False,
        readonly=True,
        default="New",
    )

    name = fields.Char(
        string="Student Name",
        required=True,
    )

    image = fields.Image(
        string="Photo",
    )

    date_of_birth = fields.Date(
        string="Date of Birth",
    )

    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
        default="male",
    )

    phone = fields.Char(
        string="Phone",
    )

    email = fields.Char(
        string="Email",
    )

    address = fields.Text(
        string="Address",
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

    department_id = fields.Many2one(
        "university.department",
        string="Department",
        required=True,
    )

    classroom_id = fields.Many2one(
        "university.classroom",
        string="Classroom",
    )

    enrollment_ids = fields.One2many(
        "university.enrollment",
        "student_id",
        string="Enrollments",
    )

    grade_ids = fields.One2many(
        "university.grade",
        "student_id",
        string="Grades",
    )

    attendance_ids = fields.One2many(
        "university.attendance",
        "student_id",
        string="Attendance",
    )

    # =====================================================
    # STATISTICS
    # =====================================================

    enrollment_count = fields.Integer(
        compute="_compute_count",
    )

    grade_count = fields.Integer(
        compute="_compute_count",
    )

    attendance_count = fields.Integer(
        compute="_compute_count",
    )

    # =====================================================
    # COMPUTE
    # =====================================================

    @api.depends(
        "enrollment_ids",
        "grade_ids",
        "attendance_ids",
    )
    def _compute_count(self):
        for rec in self:
            rec.enrollment_count = len(rec.enrollment_ids)
            rec.grade_count = len(rec.grade_ids)
            rec.attendance_count = len(rec.attendance_ids)

    # =====================================================
    # SQL CONSTRAINT
    # =====================================================

    _sql_constraints = [
        (
            "student_code_unique",
            "unique(student_code)",
            "Student code already exists!",
        ),
        (
            "student_email_unique",
            "unique(email)",
            "Email already exists!",
        ),
    ]

    # =====================================================
    # CREATE
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("student_code", "New") == "New":
                vals["student_code"] = (
                    self.env["ir.sequence"].next_by_code(
                        "university.student"
                    )
                    or "New"
                )

        return super().create(vals_list)

    # =====================================================
    # SMART BUTTON
    # =====================================================

    def action_enrollments(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Enrollments",
            "res_model": "university.enrollment",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
        }

    def action_grades(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Grades",
            "res_model": "university.grade",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
        }

    def action_attendance(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Attendance",
            "res_model": "university.attendance",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
        }
