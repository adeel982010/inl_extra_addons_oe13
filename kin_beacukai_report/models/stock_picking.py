from odoo import fields, api, models
from datetime import datetime
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class stock_picking(models.Model):
    _inherit = "stock.picking"

    move_line_ids = fields.One2many('stock.move.line', 'picking_id', 'Operations', copy=True)

    no_dokumen = fields.Char(string="No Pendaftaran", default="-")
    jenis_dokumen = fields.Selection([('Non BC', 'Non BC'), ('BC 1.6', 'BC 1.6'), ('BC 2.3', 'BC 2.3'), ('BC 2.5', 'BC 2.5'), ('BC 2.6.2', 'BC 2.6.2'), ('BC 2.6.1', 'BC 2.6.1'), (
        'BC 2.7', 'BC 2.7'), ('BC 3.0', 'BC 3.0'), ('BC 3.3', 'BC 3.3'), ('BC 4.0', 'BC 4.0'), ('BC 4.1', 'BC 4.1')], 'Jenis BC', default='Non BC')
    tanggal_dokumen = fields.Date(
        'Tanggal Dokumen', default=lambda *a: datetime.today().date())
    no_aju = fields.Char(string="No Pengajuan")
    # no_invoice = fields.Char(string="No Invoice")
    # tanggal_invoice = fields.Date(
    #     'Tanggal Invoice', default=lambda *a: datetime.today().date())
    tipe_kirim = fields.Selection(
        [('transfer', 'Transfer'), ('lokal', 'Lokal'), ('export', 'Export')], 'Tipe Pengiriman', default='')
    hs_code = fields.Char(string="HS Code")
    dok_pelengkap_ids = fields.One2many('stock.picking.document', 'picking_id', string='Dokumen Pelengkap', copy=True)
    # driver_name = fields.Char(string="Nama Supir")
    # no_karcis_timbangan = fields.Char(string="No Karcis Timbangan")
    # no_surat_jalan = fields.Char(string="No Surat Jalan")

    # ada di modul purchase_stock
    # purchase_id = fields.Many2one('purchase.order', "Purchase Order")
    # ada di modul sale_stock
    # sale_id = fields.Many2one('sale.order', "Sale Order")
    currency_id = fields.Many2one('res.currency', "Currency",
                                  compute="_compute_currency", readonly=False, store=True)

    @api.depends('purchase_id', 'sale_id')
    def _compute_currency(self):
        for row in self:
            if row.sale_id:
                row.currency_id = row.sale_id.pricelist_id.currency_id

            if row.purchase_id:
                row.currency_id = row.purchase_id.currency_id
