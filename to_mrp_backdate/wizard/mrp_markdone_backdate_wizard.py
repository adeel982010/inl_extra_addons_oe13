from odoo import fields, models


class MrpMarkdoneBackdateWizard(models.TransientModel):
    _name = 'mrp.markdone.backdate.wizard'
    _inherit = 'abstract.inventory.backdate.wizard'
    _description = 'MRP Mark Done Backdate Wizard'

    date = fields.Datetime(string='Date Done')
    mrp_order_id = fields.Many2one('mrp.production', string="Manufacturing Order", required=True, ondelete='cascade')

    def process(self):
        self.ensure_one()
        date = fields.Date.context_today(self, self.date)
        return self.mrp_order_id.with_context(
            manual_validate_date_time=self.date,
            force_period_date=date,
            ignore_backdate_wizard_call=True).button_mark_done()
