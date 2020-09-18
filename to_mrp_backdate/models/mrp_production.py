from odoo import models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def post_inventory(self):
        ctx = dict(self._context or {})
        # somewhere this is called with multi in self, so we need to fallback to the default behaviour in such the case
        if not ctx.get('ignore_backdate_wizard_call', False) and not ctx.get('manual_validate_date_time') and self.env.user.has_group('to_backdate.group_backdate') and not len(self) > 1:
            view = self.env.ref('to_mrp_backdate.mrp_inventory_backdate_wizard_form_view')
            ctx.update({'default_mrp_order_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mrp.inventory.backdate.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }
        return super(MrpProduction, self).post_inventory()

    def button_mark_done(self):
        manual_validate_date_time = self._context.get('manual_validate_date_time')
        if not manual_validate_date_time and self.env.user.has_group('to_backdate.group_backdate'):
            view = self.env.ref('to_mrp_backdate.mrp_markdone_backdate_wizard_form_view')
            ctx = dict(self._context or {})
            ctx.update({'default_mrp_order_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mrp.markdone.backdate.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }
        res = super(MrpProduction, self).button_mark_done()
        if manual_validate_date_time:
            done_order_ids = self.filtered(lambda o: o.state == 'done')
            if done_order_ids:
                done_order_ids.write({
                    'date_finished': manual_validate_date_time,
                    })
        return res
