from odoo import models, fields


class AccountStatementImportFileFormat(models.Model):
    _name = "account.statement.import.file.format"
    _description = "Bank Statement Import file format"

    name = fields.Char(required=True, )
    parser_model_name = fields.Char(required=True, )
