from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    def unblock(self):
        manual_validate_date_time = self._context.get('manual_validate_date_time', False)
        if not manual_validate_date_time:
            return super(MrpWorkcenter, self).unblock()

        self.ensure_one()
        if self.working_state != 'blocked':
            raise UserError(_("It has been unblocked already. "))

        date_end = manual_validate_date_time or fields.Datetime.now()
        times = self.env['mrp.workcenter.productivity'].search([('workcenter_id', '=', self.id), ('date_end', '=', False)])
        times.write({'date_end': date_end})
        return {'type': 'ir.actions.client', 'tag': 'reload'}
