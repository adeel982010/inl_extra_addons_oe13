from odoo import fields, api, models
from datetime import datetime
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class product_category(models.Model):
    _inherit = "product.category"

    report_type = fields.Selection([('bahan_baku', 'Bahan Baku dan Bahan Penolong'), ('barang_jadi', 'Barang Jadi dan Barang Setengah Jadi'), (
        'barang_sisa', 'Barang Sisa dan Scrap'), ('mesin', 'Mesin dan Peralatan Kantor')], 'Type of Report Category')
