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


class BebanAdministrasiReport(models.TransientModel):
    _name = 'beban.administrasi.report'

    name = fields.Char(string='Name', default="Beban Administrasi")
    date_from = fields.Date(string='Date Start', required=True, )
    date_to = fields.Date(string='Date End', required=True, )
    account_move_lines = fields.Many2many(
        comodel_name='account.move.line',
        relation='beban_administrasi_report_account_move_line_rel',
        column1='wizard_id',
        column2='produk_id',
        string='Account Move Lines'
    )
    to_this_month_move_lines = fields.Many2many(
        comodel_name='account.move.line',
        relation='beban_administrasi_report_account_move_line_to_this_month_rel',
        column1='wizard_id',
        column2='produk_id',
        string='To this month account move lines'
    )
    # carrier_xlsx_document = fields.Binary(string='Excel File')
    # carrier_xlsx_document_name = fields.Char(string='Doc Name', default='0')

    def get_accounts(self, report_id):
        report_format_obj = self.env.ref(report_id)

        if report_format_obj.account_type == 'account':
            account_ids = report_format_obj.account_account_ids
        else:
            account_ids = self.env['account.account'].search(
                [('user_type_id', 'in', report_format_obj.account_type_ids.ids)]) .account_account_ids

        return account_ids

    def get_current_period_move_lines(self, accounts):
        return self.env['account.move.line'].search([
            '&', '&', '&',
            ('parent_state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id', 'in', accounts.ids)
        ])

    def get_this_year_move_lines(self, accounts):
        last_year_end_date = datetime(datetime.today(
        ).year-1, int(self.env.user.company_id.fiscalyear_last_month), int(self.env.user.company_id.fiscalyear_last_day))

        # fiscalyear_end = datetime.strptime(fiscalyear_end_str, '%m/%d/%y')
        return self.env['account.move.line'].search([
            '&', '&', '&',
            ('parent_state', '=', 'posted'),
            ('date', '>', last_year_end_date),
            ('date', '<=', self.date_to),
            ('account_id', 'in', accounts.ids)
        ])

    def generate_report_data(self):
        account_ids = self.get_accounts(
            'accounting_custom_report_mod.accounting_custom_beban_administrasi_report')

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
            'accounting_custom_report_mod.beban_administrasi_report_action').read()[0]

        return action

    def generate_pdf(self):
        self.generate_report_data()

        action = {
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'string': _(' Beban Administrasi'),
            'name': 'beban_administrasi_report_action',
            'report_name': 'accounting_custom_report_mod.beban_administrasi_report_template',
            'file': 'accounting_custom_report_mod.beban_administrasi_report_template',
            'res_model': 'beban.administrasi.report',
            'paperformat_id': self.env.ref('accounting_custom_report_mod.accounting_custom_report_portrait_format').id,
            'res_id': self.id

        }

        return action

    def generate_excel(self):
        self.generate_report_data()

        data = {
            'date_from': self.date_from.strftime("%d/%m/%Y"),
            'date_to': self.date_to.strftime("%d/%m/%Y"),
            'res_id': self.id
        }

        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'beban.administrasi.report',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'beban_administrasi_Report_' + str(self.date_from) + '_' + str(self.date_to),
                     }
        }

    def get_xlsx_report(self, data, response):
        report_obj = self.env['beban.administrasi.report'].search(
            [('id', '=', data['res_id'])], limit=1)

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

        total_number_row_format = workbook.add_format(
            {'num_format': '#,##0.00', 'bold': True, 'top': 1, 'bottom': 1, 'left': 1, 'right': 1})

        ref_col_width = 10  # 10
        desc_col_width = 10  # 80
        this_month_col_width = 10  # 25
        to_this_month_col_width = 10  # 25

        # txt = workbook.add_format({'font_size': '10px'})
        # sheet.merge_range('B2:I3', 'EXCEL REPORT', head)
        sheet.merge_range('B2:E2', self.env.user.company_id.name, sub_head)
        sheet.merge_range('B3:E3', 'Beban Administrasi', head)
        sheet.merge_range(
            'B4:E4', data['date_from'] + ' - ' + data['date_to'], sub_head)
        sheet.write('B6', 'Ref', table_head)
        sheet.write('C6', 'Uraian', table_head)
        sheet.write('D6', 'Bulan ini', table_head)
        sheet.write('E6', 'S/d. bulan ini', table_head)

        # table content
        # BEBAN ADMINISTRASI
        accounts = self.get_accounts(
            'accounting_custom_report_mod.accounting_custom_beban_administrasi_report')
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

            if ml_balance != '':
                ml_balance_frmt = "{:,.2f}".format(float(ml_balance))
                if len(ml_balance_frmt) > this_month_col_width:
                    this_month_col_width = len(ml_balance_frmt) + 5

            if tth_ml != '':
                tth_ml_frmt = "{:,.2f}".format(float(tth_ml))
                if len(tth_ml_frmt) > to_this_month_col_width:
                    to_this_month_col_width = len(tth_ml_frmt) + 5

        # Total
        sheet.merge_range(curr_row, 1, curr_row,
                          curr_col+1, 'Jumlah Beban Administrasi', table_head)
        sheet.write(curr_row, curr_col+2,
                    sum(report_obj.account_move_lines.mapped('balance')), total_number_row_format)
        sheet.write(curr_row, curr_col+3,
                    sum(report_obj.to_this_month_move_lines.mapped('balance')), total_number_row_format)

        curr_row = curr_row + 1

        # BEBAN PENYUSUTAAN
        penyusutan_accounts = self.get_accounts(
            'accounting_custom_report_mod.accounting_custom_beban_penyusutan_report')
        if penyusutan_accounts:
            for acc in penyusutan_accounts:
                sheet.write(curr_row, curr_col, acc.code, number_row_format)
                sheet.write(curr_row, curr_col+1, acc.name, number_row_format)

                current_period_move_lines = report_obj.get_current_period_move_lines(penyusutan_accounts).filtered(
                    lambda x: x.account_id.id == acc.id)
                this_year_move_lines = report_obj.get_this_year_move_lines(penyusutan_accounts).filtered(
                    lambda x: x.account_id.id == acc.id)

                ml_balance = sum(current_period_move_lines.mapped('balance'))
                if ml_balance == 0:
                    ml_balance = ''
                sheet.write(curr_row, curr_col+2, ml_balance,
                            number_row_format)

                tth_ml = sum(this_year_move_lines.mapped('balance'))
                if tth_ml == 0:
                    tth_ml = ''
                sheet.write(curr_row, curr_col+3, tth_ml, number_row_format)

                curr_row = curr_row + 1

                # getting column width
                if len(str(acc.code)) > ref_col_width:
                    ref_col_width = len(str(acc.code)) + 5
                if len(str(acc.name)) > desc_col_width:
                    desc_col_width = len(str(acc.name)) + 5

                if ml_balance != '':
                    ml_balance_frmt = "{:,.2f}".format(float(ml_balance))
                    if len(ml_balance_frmt) > this_month_col_width:
                        this_month_col_width = len(ml_balance_frmt) + 5

                if tth_ml != '':
                    tth_ml_frmt = "{:,.2f}".format(float(tth_ml))
                    if len(tth_ml_frmt) > to_this_month_col_width:
                        to_this_month_col_width = len(tth_ml_frmt) + 5

            # Total Beban Bersih
            sheet.merge_range(curr_row, 1, curr_row,
                              curr_col+1, 'Jumlah Beban Administrasi Bersih', table_head)
            sheet.write(curr_row, curr_col+2,
                        sum(report_obj.account_move_lines.mapped('balance')) + sum(report_obj.get_current_period_move_lines(penyusutan_accounts).mapped('balance')), total_number_row_format)
            sheet.write(curr_row, curr_col+3,
                        sum(report_obj.to_this_month_move_lines.mapped('balance')) + + sum(report_obj.get_this_year_move_lines(penyusutan_accounts).mapped('balance')), total_number_row_format)

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
