from odoo import fields, models


class MrpInventoryBackdateWizard(models.TransientModel):
    _name = 'mrp.inventory.backdate.wizard'
    _inherit = 'abstract.inventory.backdate.wizard'
    _description = 'MRP Inventory Backdate Wizard'

    date = fields.Datetime(string='Inventory Date')
    mrp_order_id = fields.Many2one('mrp.production', string="Manufacturing Order", required=True, ondelete='cascade')

    def process(self):
        self.ensure_one()
        date = fields.Date.context_today(self, self.date)
        return self.mrp_order_id.with_context(manual_validate_date_time=self.date, force_period_date=date).post_inventory()
