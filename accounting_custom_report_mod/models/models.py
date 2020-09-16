# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class inl_beban_penjualan_report(models.Model):
#     _name = 'inl_beban_penjualan_report.inl_beban_penjualan_report'
#     _description = 'inl_beban_penjualan_report.inl_beban_penjualan_report'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
