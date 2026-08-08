# -*- coding: utf-8 -*-

from openai import OpenAI


class SchoolAIService:

    def __init__(self, api_key):

        if not api_key:
            raise ValueError(
                "Chưa cấu hình OpenAI API Key."
            )

        self.client = OpenAI(
            api_key=api_key
        )

    def ask(self, question, context=""):

        if not question:
            return "Vui lòng nhập câu hỏi."

        system_prompt = """
Bạn là AI Assistant của hệ thống University ERP.

Nhiệm vụ:

- Trả lời bằng tiếng Việt.
- Trả lời dựa trên dữ liệu được cung cấp.
- Không tự bịa số liệu.
- Nếu dữ liệu không đủ thì phải nói rõ.
- Có thể phân tích:
  + Sinh viên
  + Giáo viên
  + Khoa
  + Môn học
  + Lớp học
  + Đăng ký
  + Điểm
  + Điểm danh
  + Lịch học

Quy tắc:

1. Ưu tiên dữ liệu ERP.
2. Không tự tạo dữ liệu không tồn tại.
3. Khi phân tích điểm phải dựa vào dữ liệu điểm thực tế.
4. Trình bày câu trả lời rõ ràng.
"""

        user_prompt = f"""
DỮ LIỆU UNIVERSITY ERP:

{context}

CÂU HỎI:

{question}
"""

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            instructions=system_prompt,
            input=user_prompt,
        )

        return response.output_text