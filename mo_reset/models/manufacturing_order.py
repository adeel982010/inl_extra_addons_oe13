from odoo import api, fields, models


class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    # product_uom_id = fields.Many2one(
    #     'uom.uom', 'Product Unit of Measure',
    #     oldname='product_uom', readonly=True, required=True,
    #     states={'draft': [('readonly', False)]})

    # state = fields.Selection(selection_add=[('draft', 'Draft')])

    def action_draft(self):
        self.move_raw_ids.write({'is_done':False})
        self.move_raw_ids = False
        self.move_finished_ids = False
        self.write({'state': 'draft'})
        return True
