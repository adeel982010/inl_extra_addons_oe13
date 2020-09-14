# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Indonesia E-faktur (Kinsoft)',
    'version': '1.0',
    'description': """
        Inherit E-Faktur Menu(Indonesia)
        menambahkan field tanggal efaktur
        laporan yang ditampilkan sudah dikurangi dengan retur
    """,
    "author": 'Kinsoft Indonesia, Kikin Kusumah',
    "website": 'kinsoft.id',
    'category': 'Accounting',
    'depends': ['l10n_id','l10n_id_efaktur'],
    'data': [
            'views/account_move_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
}
