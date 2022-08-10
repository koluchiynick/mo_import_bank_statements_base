{
    'name': 'Import bank statements from a file base',
    'summary': 'Import bank statements from a file base',
    'author': 'Mikola Ostroukh',
    'license': "LGPL-3",
    'category': 'Banking addons',
    'version': '15.0.1.0.0',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/file_format_data.xml',
        'views/account_journal.xml',
        'wizard/account_statement_import_action.xml',        
    ],
}