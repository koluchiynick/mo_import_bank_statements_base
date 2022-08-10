import logging
import base64
from io import StringIO
from datetime import datetime

from odoo import models, fields
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    logger.debug('Cannot `import csv`.')


class AccountBankStatementsImportFile(models.TransientModel):
    _name = "account.bank.statement.import"
    _description = "Import bank statements from a file"
    
    def _get_default_file_format_id(self):
        return self.env["account.journal"].browse(self.env.context.get("journal_id")).default_file_format_id
    
    file_format_id = fields.Many2one(
        string="File format", 
        comodel_name="account.statement.import.file.format",
        default=_get_default_file_format_id,
    )
    import_file = fields.Binary(required=True, help="Wrap the file imported from your bank",)
    import_filename = fields.Char()
    
    def create_statement(self,transactions_list):
        statement_vals = {
            'name': 'Statement Of ' + str(datetime.today().date()).replace('-','/'),
            'journal_id': self.env.context.get('active_id'),
            'line_ids': transactions_list
        }
        statement = self.env['account.bank.statement'].create(statement_vals)                
        return statement
        
    def import_file_button(self):
        self.ensure_one()
        logger.info("Start to import bank statement file %s", self.import_filename)
        logger.info("File format %s", self.file_format_id.parser_model_name)
        
        transactions_list = self.env[self.file_format_id.parser_model_name].parse(self.import_file, self.import_filename)
        if len(transactions_list) == 0:
            raise UserError(
                (
                    "The file does not contain transactions on this account"
                )
            )
        statement = self.create_statement(transactions_list)
        if self.env.context.get("return_regular_interface_action"):
            action = (
                self.env.ref("account.action_bank_statement_tree").sudo().read([])[0]
            )
            action.update(
                {
                    "view_mode": "form,tree",
                    "views": False,
                    "res_id": statement.id,
                }
            )
            return action
    