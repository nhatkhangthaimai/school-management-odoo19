from odoo import http
from odoo.http import request


class SchoolController(http.Controller):

    @http.route('/api/students', auth='user', type='json')
    def students(self):

        students = request.env["university.student"].search([])

        result = []

        for student in students:
            result.append({
                "id": student.id,
                "student_code": student.student_code,
                "name": student.name,
                "email": student.email,
            })

        return result