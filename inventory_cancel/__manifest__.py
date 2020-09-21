# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Cancel Inventory Adjustment',
    'version': '1.0',
    'author': 'Craftsync Technologies',
    'category': 'stock',
    'maintainer': 'Craftsync Technologies',

    'summary': """Cancel Inventory Adjustment app is helpful plugin to cancel processed Stock Inventory. Cancellation of Stock Inventory includes operations like cancel Stock Move, Cancel Delivery Order, Cancel Inventory Lines.""",

    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support': 'info@craftsync.com',
    'depends': ['stock', 'account'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/view_inventory.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 9.99,
    'currency': 'EUR',

}
