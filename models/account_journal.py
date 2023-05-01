from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    default_file_format_id = fields.Many2one(
        comodel_name="account.statement.import.file.format", )

    def import_account_statement(self):
        action = (self.env.ref(
            "mo_import_bank_statements_base.account_bank_statement_import_action"
        ).sudo().read()[0])
        action["context"] = {"journal_id": self.id}
        return action

    def __get_bank_statements_available_sources(self):
        rslt = super().__get_bank_statements_available_sources()
        rslt.append(("file_import_format", ("File Import")))
        return rslt
