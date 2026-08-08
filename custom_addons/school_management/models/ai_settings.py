from odoo import fields, models


class SchoolAISettings(models.TransientModel):
    _inherit = "res.config.settings"

    school_ai_openai_api_key = fields.Char(
        string="OpenAI API Key",
        config_parameter="school_management.openai_api_key",
    )

    school_ai_openai_model = fields.Char(
        string="AI Model",
        config_parameter="school_management.openai_model",
        default="gpt-4.1-mini",
    )