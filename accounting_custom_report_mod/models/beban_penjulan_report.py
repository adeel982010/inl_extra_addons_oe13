from odoo import fields, models, api, _
from odoo.exceptions import UserError
from pprint import pprint
from datetime import datetime
import json
import base64
import io
from odoo.http import content_disposition, request
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    # TODO saas-17: remove the try/except to directly import from misc
    import xlsxwriter


class BebanPenjualanReport(models.TransientModel):
    _name = 'beban.penjualan.report'

    name = fields.Char(string='Name', default="Beban Penjualan")
    date_from = fields.Date(string='Date Start', required=True, )
    date_to = fields.Date(string='Date End', required=True, )
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
    # carrier_xlsx_document = fields.Binary(string='Excel File')
    # carrier_xlsx_document_name = fields.Char(string='Doc Name', default='0')

    def get_accounts(self):
        format_beban_penjualan_report = self.env.ref(
            'accounting_custom_report_mod.accounting_custom_beban_penjualan_report')

        if format_beban_penjualan_report.account_type == 'account':
            account_ids = format_beban_penjualan_report.account_account_ids
        else:
            account_ids = self.env['account.account'].search(
                [('user_type_id', 'in', format_beban_penjualan_report.account_type_ids.ids)]) .account_account_ids

        return account_ids

    def generate_report_data(self):
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
        last_year_end_date = datetime(datetime.today(
        ).year-1, int(self.env.user.company_id.fiscalyear_last_month), int(self.env.user.company_id.fiscalyear_last_day))

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

    def process_wizard(self):

        self.generate_report_data()

        action = self.env.ref(
            'accounting_custom_report_mod.beban_penjualan_report_action').read()[0]

        return action

    def generate_pdf(self):
        self.generate_report_data()

        action = {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'string': _(' Beban Penjualan'),
            'name': 'beban_penjualan_report_action',
            'report_name': 'accounting_custom_report_mod.beban_penjualan_report_template',
            'file': 'accounting_custom_report_mod.beban_penjualan_report_template',
            'res_model': 'beban.penjualan.report',
            'paperformat_id': self.env.ref('accounting_custom_report_mod.accounting_custom_report_portrait_format').id,
            'res_id': self.id

        }

        return action

    def generate_excel(self):
        print('**** Wizard ID : ' + str(self.id))
        self.generate_report_data()

        data = {
            'date_from': self.date_from.strftime("%d/%m/%Y"),
            'date_to': self.date_to.strftime("%d/%m/%Y"),
            'res_id': self.id
        }

        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'beban.penjualan.report',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Beban_Penjualan_Report_' + str(self.date_from) + '_' + str(self.date_to),
                     }
        }

    def get_xlsx_report(self, data, response):
        report_obj = self.env['beban.penjualan.report'].search(
            [('id', '=', data['res_id'])], limit=1)

        print('Account move lines')
        pprint(report_obj.account_move_lines)

        print('to this month Account move lines')
        pprint(report_obj.to_this_month_move_lines)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': '10pt'})
        curr_row = 6
        curr_col = 1

        head = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': True, 'font_size': '10pt'})
        sub_head = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bold': True, 'font_size': '8pt'})

        table_head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10pt', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})

        number_row_format = workbook.add_format(
            {'num_format': '#,##0.00', 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})

        ref_col_width = 0  # 10
        desc_col_width = 0  # 80
        this_month_col_width = 0  # 25
        to_this_month_col_width = 0  # 25

        # txt = workbook.add_format({'font_size': '10px'})
        # sheet.merge_range('B2:I3', 'EXCEL REPORT', head)
        sheet.merge_range('B2:E2', self.env.user.company_id.name, sub_head)
        sheet.merge_range('B3:E3', 'Beban Penjualan', head)
        sheet.merge_range(
            'B4:E4', data['date_from'] + ' - ' + data['date_to'], sub_head)
        sheet.write('B6', 'Ref', table_head)
        sheet.write('C6', 'Uraian', table_head)
        sheet.write('D6', 'Bulan ini', table_head)
        sheet.write('E6', 'S/d. bulan ini', table_head)

        # table content
        accounts = self.get_accounts()
        for acc in accounts:
            sheet.write(curr_row, curr_col, acc.code, number_row_format)
            sheet.write(curr_row, curr_col+1, acc.name, number_row_format)

            ml = report_obj.account_move_lines.filtered(
                lambda x: x.account_id.id == acc.id)
            to_this_month_ml = report_obj.to_this_month_move_lines.filtered(
                lambda x: x.account_id.id == acc.id)

            ml_balance = sum(ml.mapped('balance'))
            if ml_balance == 0:
                ml_balance = ''
            sheet.write(curr_row, curr_col+2, ml_balance,
                        number_row_format)

            tth_ml = sum(to_this_month_ml.mapped('balance'))
            if tth_ml == 0:
                tth_ml = ''
            sheet.write(curr_row, curr_col+3, tth_ml, number_row_format)

            curr_row = curr_row + 1

            # getting column width
            if len(str(acc.code)) > ref_col_width:
                ref_col_width = len(str(acc.code)) + 5
            if len(str(acc.name)) > desc_col_width:
                desc_col_width = len(str(acc.name)) + 5
            if len(str(ml_balance)) > this_month_col_width:
                this_month_col_width = len(str(ml_balance)) + 5
            if len(str(tth_ml)) > to_this_month_col_width:
                to_this_month_col_width = len(str(tth_ml)) + 5

        # Total
        sheet.merge_range(curr_row, 1, curr_row,
                          curr_col+1, 'Jumlah', table_head)
        sheet.write(curr_row, curr_col+2,
                    sum(report_obj.account_move_lines.mapped('balance')), number_row_format)
        sheet.write(curr_row, curr_col+3,
                    sum(report_obj.to_this_month_move_lines.mapped('balance')), number_row_format)

        # set column width
        sheet.set_column(0, 0, 3)
        sheet.set_column(1, 1, ref_col_width)
        sheet.set_column(2, 2, desc_col_width)
        sheet.set_column(3, 3, this_month_col_width)
        sheet.set_column(4, 4, to_this_month_col_width)

        workbook.close()
        output.seek(0)

        response.stream.write(output.read())

        output.close()
        