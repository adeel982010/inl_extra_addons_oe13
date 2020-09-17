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
        [("account", "Account"), ("account.type", "Account Type"), ('group', 'Account Group'), ('tag', 'Account Tag')], string='Account Type', required=True, )
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
        column2='type_id',
        string='Account Types'
    )
    account_by_group_ids = fields.Many2many(
        comodel_name='account.group',
        relation='accounting_custom_report_account_account_group_rel',
        column1='report_id',
        column2='group_id',
        string='Account Groups'
    )
    account_by_tag_ids = fields.Many2many(
        comodel_name='account.account.tag',
        relation='accounting_custom_report_account_account_tag_rel',
        column1='report_id',
        column2='tag_id',
        string='Account Tags'
    )

    # @api.onchange('account_type')
    # def _account_type_onchange(self):
    #     # self.account_account_ids = [(5)]
    #     # self.account_type_ids = [(5)]
    #     # self.account_by_group_ids = [(5)]
    #     # self.account_by_tag_ids = [(5)]

    #     self.write({
    #         'account_account_ids' :  [(5)],
    #     'account_type_ids' :  [(5)],
    #     'account_by_group_ids' :  [(5)],
    #     'account_by_tag_ids' :  [(5)],
    #     })

    def get_accounts(self):
        if self.account_type == 'account':
            return self.account_account_ids
        elif self.account_type == 'account.type':
            return self.env['account.account'].search([('user_type_id', 'in', self.account_type_ids.ids)])
        elif self.account_type == 'group':
            return self.env['account.account'].search([('group_id', 'in', self.account_by_group_ids.ids)])
        elif self.account_type == 'tag':
            return self.env['account.account'].search([('tag_ids', 'in', self.account_by_tag_ids.ids)])
