# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cancel Manufacturing Order',
    'version' : '1.0',
    'author':'Craftsync Technologies',
    'category': 'Manufacturing',
    'maintainer': 'Craftsync Technologies',
   
    'summary': """Cancel manufacturings Order  cancel processed manufacturing order Cancellation of manufacturing order  cancel mrp cancel manufacturing manufacturing cancel mrp cancel mo cancel cancel mo canel bom cancel work orders work order cancel  cancel inventory moves inventory moves cancel Cancel mrp Cancel manufacturing manufacturing Cancel mrp Cancel mo Cancel Cancel mo Cancel bom Cancel work orders work order Cancel  Cancel inventory moves inventory moves Cancel Cancel Mrp Cancel Manufacturing Manufacturing Cancel Mrp Cancel Mo Cancel Cancel Mo Cancel Bom Cancel Work Orders Work Order Cancel  Cancel Inventory Moves Inventory Moves Cancel cancel manufacturing order manufacturing order cancel Cancel Manufacturing Order Manufacturing Order Cancel Cancel manufacturing Orders manufacturing Orders Cancel Cancel MO MO Cancel MO CANCEL mo cancel cancel mo """,

    'website': 'https://www.craftsync.com/',
    'license': 'OPL-1',
    'support':'info@craftsync.com',
    'depends' : ['mrp','account'],
    'data': [
        'views/res_config_settings_views.xml',
	    'views/view_manufacturing_order.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screen.png'],
    'price': 34.99,
    'currency': 'EUR',

}
