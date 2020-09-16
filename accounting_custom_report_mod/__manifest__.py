# -*- coding: utf-8 -*-
{
    'name': "Accounting Custom Report Mod",

    'summary': """
        Accounting custom report""",

    'description': """
        Accounting custom report : 
        1. Beban Penjualan
    """,

    'author': "butirpadi",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/custom_report_data.xml',
        'views/accounting_custom_report_format_view.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
}
