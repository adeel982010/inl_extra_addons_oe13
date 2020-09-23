# -*- coding: utf-8 -*-
{
    'name': "Customize Odoo for PT. Industri Nabati Lestari",

    'summary': """
    customize my odoo.
        """,

    'description': """
        Customize Odoo:
        - Expense (Show Expense Journal)
        - Partner (Cannot Duplicate Internal Reference field)
        - Product (Cannot Duplicate Internal Reference field)
         
    """,

    'author': 'Kinsoft Indonesia, Kikin Kusumah',
    'website': 'kinsoft.id',
    'support': 'kinsoft.indonesia@gmail.com',

    'category': 'Accounting',
    'version': '1',

    'depends': ['purchase','sale','account'],

    'data': [
        'views/purchase_views.xml',
        'views/sale_order_views.xml',
        'views/account_view.xml',
    ],
    'application': True,
    'installable': True,
}
