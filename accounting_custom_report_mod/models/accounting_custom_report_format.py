from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountingCustomReportFormat(models.Model):
    _name = 'accounting.custom.report.format'

    name = fields.Char(string='Report Name', required=True, )
    parent_report_id = fields.Many2one(
        'accounting.custom.report.format', string='Parent Report')
    child_report_ids = fields.One2many(
        'accounting.custom.report.format', 'parent_report_id', string='Sub Reports')
    account_type = fields.Selection(
        [("account", "Account"), ("account.type", "Account Type")], string='Account Type', required=True, )
    account_account_ids = fields.Many2many(
        comodel_name='account.account',
        relation='accounting_custom_report_account_account_rel',
        column1='report_id',
        column2='account_id',
        string='Accounts'
    )
    account_type_ids = fields.Many2many(
        comodel_name='account.account.type',
        relation='accounting_custom_report_account_account_type_rel',
        column1='report_id',
        column2='account_id',
        string='Account Types'
    )
