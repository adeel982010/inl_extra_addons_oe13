from odoo import fields, models, api, _
from odoo.exceptions import UserError
from pprint import pprint


class BebanPenjualanReport(models.TransientModel):
    _name = 'beban.penjualan.report'

    name = fields.Char(string='Name', default="Beban Penjualan")
    date_from = fields.Date(string='Date Start')
    date_to = fields.Date(string='Date End')
    account_move_lines = fields.Many2many(
        comodel_name='account.move.line',
        relation='beban_penjualan_report_account_move_line_rel',
        column1='wizard_id',
        column2='produk_id',
        string='Account Move Lines'
    )

    def process_wizard(self):
        format_beban_penjualan_report = self.env.ref(
            'accounting_custom_report_mod.accounting_custom_beban_penjualan_report')

        if format_beban_penjualan_report.account_type == 'account':
            account_ids = format_beban_penjualan_report.account_account_ids.ids
        else:
            account_ids = self.env['account.account'].search(
                [('user_type_id', 'in', format_beban_penjualan_report.account_type_ids.ids)]) .account_account_ids.ids

        self.account_move_lines = self.env['account.move.line'].search([
            '&', '&', '&',
            ('parent_state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id', 'in', account_ids)
        ])

        print('Process Wizard')
