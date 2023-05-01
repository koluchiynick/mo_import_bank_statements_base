import logging
import tempfile
import binascii

from odoo import models
from odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)

try:
    import dbf
except ImportError:
    logger.debug('Cannot `import dbf`.')


class AccountStatementImportPumbDbf(models.TransientModel):
    _name = "account.statement.import.pumb.dbf"
    _description = "Import bank statements PUMB DBF file format"

    def get_partner(self, edrpou_partner, name_partner):
        try:
            partner = self.env['res.partner'].search([('mo_edrpou', '=',
                                                       edrpou_partner)])
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
        journal = self.env["account.journal"].browse(
            self.env.context.get("journal_id"))
        journal_acc_number = journal.bank_account_id.acc_number

        if import_filename.lower().strip().endswith('.dbf'):
            statement = False
            try:
                fp = tempfile.NamedTemporaryFile(delete=True, suffix=".dbf")
                fp.write(binascii.a2b_base64(import_file))
                fp.seek(0)
                table = dbf.Table(fp.name)
                table.open(dbf.READ_ONLY)
            except:
                raise UserError(("Invalid file!"))

            vals_list = []
            for row in table:
                values = {}
                if journal_acc_number == row.ACC_NUMB:
                    amount = row.CR.strip() if row.DB.strip(
                    ) == '' else '-' + row.DB.strip()
                    values.update({
                        'date':
                        row.DOC_DATE.replace('.', '-'),
                        'payment_ref':
                        row.DESCRIPT.strip(),
                        'partner_id':
                        self.get_partner(row.KOR_OKPO.strip(),
                                         row.KOR_NAME.strip()),
                        'amount':
                        amount,
                    })
                    vals_list.append((0, 0, values))
            return vals_list
        else:
            raise ValidationError(("Unsupported File Type"))
