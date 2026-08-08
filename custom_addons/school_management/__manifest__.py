{
    "name": "University ERP",
    "summary": "University Management System",
    "description": """
University ERP Management System
================================

Modules:
- Dashboard
- Department
- Teacher
- Student
- Subject
- Classroom
- Enrollment
- Grade
- Attendance
- Schedule
    """,

    "author": "Your Name",
    "website": "https://yourcompany.com",

    "category": "Education",
    "version": "1.0.0",

    "depends": [
        "base",
        "mail",
    ],

    "data": [
    "security/ir.model.access.csv",

    "data/sequence.xml",

    "views/dashboard_views.xml",
    "views/department_views.xml",
    "views/teacher_views.xml",
    "views/student_views.xml",
    "views/subject_views.xml",
    "views/classroom_views.xml",
    "views/enrollment_views.xml",
    "views/grade_views.xml",
    "views/attendance_views.xml",
    "views/schedule_views.xml",
    'views/ai_assistant_views.xml',
    "views/ai_settings_views.xml",
    "views/menu_views.xml",
],

    "installable": True,

    "application": True,

    "auto_install": False,

    "license": "LGPL-3",
}