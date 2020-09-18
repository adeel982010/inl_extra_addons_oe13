{
    'name': "Manufacturing Backdate",
    'name_vi_VN': "Sản Xuất Trong Quá Khứ",

    'summary': """
MRP backdate operations, incl. posting inventory, mark MO as done, backdate work orders""",

    'summary_vi_VN': """
Nhập ngày trong quá khứ cho sản xuất (hoàn thành lệnh, hoạt động sản xuất trong quá khứ, bút toán kho cho sản xuất trong quá khứ)
    	""",

    'description': """
Total solution for MRP backdate operations

* Posting inventory with backdate
* Inventory Accounting with backdate
* Scrap backdate
* Work Orders with backdate

  * **Start** a work order with backdate
  * **Pause** a work order with backdate
  * **Continue/Resume** a work order with backdate
  * **Block** a work order with backdate
  * **Unblock** a work order with backdate
  * **Finish** a work order with backdate


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Giải pháp toàn diện cho vấn đề nhập ngày trong quá khứ cho

* Vào sổ kho từ lệnh sản xuất với ngày trong quá khứ
* Ghi nhận phế liệu với ngày trong quá khứ
* Bút toán kế toán kho cho nguyên vật liệu và thành phẩm (bao gồm cả bán thành phẩm)
* Hoạt động sản xuất

  * **Khởi động** một hoạt động sản xuất với ngày giờ trong quá khứ
  * **Tạm dừng** một hoạt động sản xuất với ngày giờ trong quá khứ
  * **Tiếp tục/Tái khởi động** một hoạt động sản xuất với ngày giờ trong quá khứ
  * **Phong toả** một hoạt động sản xuất với ngày giờ trong quá khứ
  * **Dừng Phong toả** một hoạt động sản xuất với ngày giờ trong quá khứ
  * **Hoàn thành** một hoạt động sản xuất với ngày giờ trong quá khứ

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA)",
    'website': "https://www.tvtmarine.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'support': "support@ma.tvtmarine.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp', 'to_stock_backdate'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'wizard/mrp_inventory_backdate_wizard_views.xml',
        'wizard/mrp_markdone_backdate_wizard_views.xml',
        'wizard/mrp_workcenter_block_view.xml',
        'wizard/mrp_workorder_backdate_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
