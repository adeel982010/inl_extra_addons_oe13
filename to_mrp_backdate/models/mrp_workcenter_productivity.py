from odoo import api, fields, models


class MrpWorkcenterProductivity(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    backdate = fields.Datetime(string='Backdate', help="If filled, this date and time will be used instead"
                               " of the current date and time")

    def button_block(self):
        self.ensure_one()
        if self.backdate:
            super(MrpWorkcenterProductivity, self.with_context(manual_validate_date_time=self.backdate)).button_block()
        else:
            super(MrpWorkcenterProductivity, self).button_block()

