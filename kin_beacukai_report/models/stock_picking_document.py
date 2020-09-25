from odoo import api, fields, models, _
from datetime import datetime


class StockPickingDocument(models.Model):
    _name = 'stock.picking.document'
    _description = "Dokumen Pelengkap"

    name = fields.Char('Nomor', required=True)
    sequence = fields.Integer(default=10)
    picking_id = fields.Many2one(
        'stock.picking', 'Stock Picking', auto_join=True)
    picking_name = fields.Char(string='Number', related='picking_id.name', store=True, index=True)
    doc_type = fields.Selection(
        [('delivery_order', 'Delivery Order'), ('invoice', 'Invoice'), ('packing_list', 'Packing List')], 'Document Type', default='')
    date = fields.Date(
        'Date', default=lambda *a: datetime.today().date())