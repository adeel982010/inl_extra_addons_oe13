from odoo import fields, models, api, _
from odoo.exceptions import UserError
from pprint import pprint
from datetime import datetime


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
    to_this_month_move_lines = fields.Many2many(
        comodel_name='account.move.line',
        relation='beban_penjualan_report_account_move_line_to_this_month_rel',
        column1='wizard_id',
        column2='produk_id',
        string='To this month account move lines'
    )

    def get_accounts(self):
        format_beban_penjualan_report = self.env.ref(
            'accounting_custom_report_mod.accounting_custom_beban_penjualan_report')

        if format_beban_penjualan_report.account_type == 'account':
            account_ids = format_beban_penjualan_report.account_account_ids
        else:
            account_ids = self.env['account.account'].search(
                [('user_type_id', 'in', format_beban_penjualan_report.account_type_ids.ids)]) .account_account_ids

        return account_ids

    def process_wizard(self):

        account_ids = self.get_accounts()

        self.account_move_lines = self.env['account.move.line'].search([
            '&', '&', '&',
            ('parent_state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id', 'in', account_ids.ids)
        ])

        # get to this month move lines

        # get fiscal year end month
        # fiscalyear_end_str = str(self.env.user.company_id.fiscalyear_last_month) + '/' + str(self.env.user.company_id.fiscalyear_last_day) + '/' + str(datetime.today().year)
        last_year_end_date = datetime(datetime.today().year-1,int(self.env.user.company_id.fiscalyear_last_month),int(self.env.user.company_id.fiscalyear_last_day))
        
        print('Fiscal Year End Date')
        print(last_year_end_date)

        # fiscalyear_end = datetime.strptime(fiscalyear_end_str, '%m/%d/%y')

        self.to_this_month_move_lines = self.env['account.move.line'].search([
            '&', '&', '&',
            ('parent_state', '=', 'posted'),
            ('date', '>', last_year_end_date),
            ('date', '<=', self.date_to),
            ('account_id', 'in', account_ids.ids)
        ])

        action = self.env.ref(
            'accounting_custom_report_mod.beban_penjualan_report_action').read()[0]

        return action
