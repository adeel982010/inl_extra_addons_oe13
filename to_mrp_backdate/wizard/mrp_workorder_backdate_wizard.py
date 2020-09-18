from odoo import fields, models


class MrpWorkorderBackdateWizard(models.TransientModel):
    _name = 'mrp.workorder.backdate.wizard'
    _inherit = 'abstract.inventory.backdate.wizard'
    _description = 'MRP Workorder Backdate Wizard'

    mrp_wo_id = fields.Many2one('mrp.workorder', string="Work Order", required=True, ondelete='cascade')
    source_action = fields.Char(string='Source Action', required=True,
                                help="The source method of mrp.workorder that called this wizard.")

    def process(self):
        self.ensure_one()
        date = fields.Date.context_today(self, self.date)
        return getattr(self.mrp_wo_id.with_context(
            manual_validate_date_time=self.date,
            force_period_date=date,
            ignore_backdate_wizard_call=True), self.source_action)()
