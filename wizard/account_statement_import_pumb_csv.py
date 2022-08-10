import logging
import base64
from io import StringIO

from odoo import models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    logger.debug('Cannot `import csv`.')


class AccountStatementImportPumbCsv(models.TransientModel):
    _name = "account.statement.import.pumb.csv"
    _description = "Import bank statements PUMB csv file format"
    
    def get_partner(self, edrpou_partner, name_partner):
        try:
            partner = self.env['res.partner'].search([('mo_edrpou', '=', edrpou_partner)])
        except:
            partner = False
        
        if partner:
            return partner.id
        
        partner = self.env['res.partner'].search([('vat', '=', name_partner)])
        if partner:
            return partner.id
        
        partner = self.env['res.partner'].search([('name', '=', name_partner)])
        return partner.id if partner else False
    
    def parse(self, import_file, import_filename):
        journal = self.env["account.journal"].browse(self.env.context.get("journal_id"))
        journal_acc_number = journal.bank_account_id.acc_number
        
        if import_filename.lower().strip().endswith('.csv'):
            statement = False
            try:
                file_data = base64.b64decode(import_file)
                csv_data = StringIO(file_data.decode("Windows-1251"))
                csv_data.seek(0)
                csv_reader = csv.DictReader(csv_data, delimiter=';')
                file_reader = []
                file_reader.extend(csv_reader)
                
            except:
                raise UserError(("Invalid file!"))
            
            vals_list = []
            for row in file_reader:
                values = {}
                if journal_acc_number == row['ACC_NUMB']:
                    amount = row["CR"] if row["DB"] == '' else '-'+row["DB"]
                    values.update({
                        'date': row["DOC_DATE"].replace('.','-'),
                        'payment_ref': row["DESCRIPT"].strip(),
                        'partner_id': self.get_partner(row["KOR_OKPO"].strip(),row["KOR_NAME"].strip()),
                        'amount': amount,
                    })
                    vals_list.append((0, 0, values))
            return vals_list            
        else:
            raise ValidationError(("Unsupported File Type"))
