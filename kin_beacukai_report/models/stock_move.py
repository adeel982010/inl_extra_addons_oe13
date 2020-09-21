from odoo import api, fields, models, _
import math
from odoo.addons import decimal_precision as dp
from pprint import pprint
from odoo.exceptions import UserError, Warning


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_price = fields.Float(
        string="Price", digits=dp.get_precision('Product Price'),
        compute="_compute_product_price", inverse='_set_product_price', readonly=False, store=True)

    subtotal_price = fields.Float(
        string="Amount", digits=(12, 2),
        compute="_compute_subtotal_price", readonly=False, store=True)

    @api.depends('purchase_line_id', 'sale_line_id')
    def _compute_product_price(self):
        # print('KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
        # print('Subtotal : ' + str(self.subtotal_price))
        for row in self:
            if row.purchase_line_id:
                # print('Price Unit : ' + str(row.purchase_line_id.price_unit))
                row.product_price = row.purchase_line_id.price_unit

            if row.sale_line_id:
                row.product_price = row.sale_line_id.price_unit
        # print('KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')

    def _set_product_price(self):
        # raise UserError(
        #     _('Please add some items to move.' + str(self.product_price)))
        for row in self:
            if not row.product_price:
                continue

    @api.depends('quantity_done', 'product_price')
    def _compute_subtotal_price(self):
        for row in self:
            row.subtotal_price = row.quantity_done * row.product_price
        # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        # print('QTY : ' + str(self.quantity_done))
        # print('Price Unit : ' + str(self.price_unit))
        # print('Subtotal : ' + str(self.subtotal_price))
        # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    no_polisi = fields.Char(string="No Polisi")
    driver_name = fields.Char(string="Nama Supir")
    no_karcis_timbangan = fields.Char(string="No Karcis Timbangan")
    no_surat_jalan = fields.Char(string="No Surat Jalan")
    bruto_from = fields.Float(
        string="Bruto (From)", digits=dp.get_precision('Stock Weight'), readonly=False, store=True)
    tarra_from = fields.Float(
        string="Tarra (From)", digits=dp.get_precision('Stock Weight'), readonly=False, store=True)
    netto_from = fields.Float(
        string="Netto (From)", digits=dp.get_precision('Stock Weight'),
        compute="_compute_netto_from", inverse='_set_netto_from', readonly=False, store=True)
    bruto = fields.Float(
        string="Bruto", digits=dp.get_precision('Stock Weight'), readonly=False, store=True)
    tarra = fields.Float(
        string="Tarra", digits=dp.get_precision('Stock Weight'), readonly=False, store=True)

    @api.depends('bruto_from', 'tarra_from')
    def _compute_netto_from(self):
        for row in self:
            row.netto_from = row.bruto_from - row.tarra_from

    def _set_netto_from(self):
        for row in self:
            if not row.netto_from:
                continue
