# -*- coding: utf-8 -*-
# from odoo import http


# class InlBebanPenjualanReport(http.Controller):
#     @http.route('/inl_beban_penjualan_report/inl_beban_penjualan_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inl_beban_penjualan_report/inl_beban_penjualan_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inl_beban_penjualan_report.listing', {
#             'root': '/inl_beban_penjualan_report/inl_beban_penjualan_report',
#             'objects': http.request.env['inl_beban_penjualan_report.inl_beban_penjualan_report'].search([]),
#         })

#     @http.route('/inl_beban_penjualan_report/inl_beban_penjualan_report/objects/<model("inl_beban_penjualan_report.inl_beban_penjualan_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inl_beban_penjualan_report.object', {
#             'object': obj
#         })
