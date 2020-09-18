from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def _prepare_backdate_wizard(self, ctx):
        view = self.env.ref('to_mrp_backdate.mrp_workorder_backdate_wizard_form_view')
        ctx.update({'default_mrp_wo_id': self.id})
        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mrp.workorder.backdate.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }

    def button_start(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if not ctx.get('ignore_backdate_wizard_call', False) and not manual_validate_date_time and self.env.user.has_group('to_backdate.group_backdate'):
            ctx.update({'default_source_action': 'button_start'})
            return self._prepare_backdate_wizard(ctx)

        # HACKING Odoo since there is no way to extend.
        # Check if any posibility to remove this hack in Odoo 13: https://github.com/odoo/odoo/pull/32669
        self.ensure_one()
        # As button_start is automatically called in the new view
        if self.state in ('done', 'cancel'):
            return True

        # Need a loss in case of the real time exceeding the expected
        timeline = self.env['mrp.workcenter.productivity']
        if self.duration < self.duration_expected:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'productive')], limit=1)
            if not len(loss_id):
                raise UserError(_("You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        else:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'performance')], limit=1)
            if not len(loss_id):
                raise UserError(_("You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))

        date_start = manual_validate_date_time or fields.Datetime.now()
        for workorder in self:
            if workorder.production_id.state != 'progress':
                workorder.production_id.write({
                    'state': 'progress',
                    'date_start': date_start,
                })
            timeline.create({
                'workorder_id': workorder.id,
                'workcenter_id': workorder.workcenter_id.id,
                'description': _('Time Tracking: ') + self.env.user.name,
                'loss_id': loss_id[0].id,
                'date_start': date_start,
                'user_id': self.env.user.id
            })
        return self.write({
            'state': 'progress',
            'date_start': date_start,
            })

    def button_finish(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if not ctx.get('ignore_backdate_wizard_call', False) and not manual_validate_date_time and self.env.user.has_group('to_backdate.group_backdate'):
            ctx.update({'default_source_action': 'button_finish'})
            return self._prepare_backdate_wizard(ctx)

        if manual_validate_date_time:
            self.write({'date_finished': manual_validate_date_time})
        return super(MrpWorkorder, self).button_finish()

    def end_previous(self, doall=False):
        """
        HACKING ODOO
        
        @param: doall:  This will close all open time lines on the open work orders when doall = True, otherwise
        only the one of the current user
        """
        # TDE CLEANME
        timeline_obj = self.env['mrp.workcenter.productivity']
        domain = [('workorder_id', 'in', self.ids), ('date_end', '=', False)]
        if not doall:
            domain.append(('user_id', '=', self.env.user.id))
        not_productive_timelines = timeline_obj.browse()

        manual_validate_date_time = self._context.get('manual_validate_date_time', fields.Datetime.now())

        for timeline in timeline_obj.search(domain, limit=None if doall else 1):
            wo = timeline.workorder_id
            if wo.duration_expected <= wo.duration:
                if timeline.loss_type == 'productive':
                    not_productive_timelines += timeline
                timeline.write({'date_end': manual_validate_date_time})
            else:
                maxdate = fields.Datetime.from_string(timeline.date_start) + relativedelta(minutes=wo.duration_expected - wo.duration)
                enddate = datetime.now()
                if maxdate > enddate:
                    timeline.write({'date_end': manual_validate_date_time})
                else:
                    timeline.write({'date_end': maxdate})
                    not_productive_timelines += timeline.copy({'date_start': maxdate, 'date_end': manual_validate_date_time})
        if not_productive_timelines:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type', '=', 'performance')], limit=1)
            if not len(loss_id):
                raise UserError(_("You need to define at least one unactive productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
            not_productive_timelines.write({'loss_id': loss_id.id})
        return True

    def end_all(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if not ctx.get('ignore_backdate_wizard_call', False) and not manual_validate_date_time and self.env.user.has_group('to_backdate.group_backdate') and not len(self) > 1:
            ctx.update({'default_source_action': 'end_all'})
            return self._prepare_backdate_wizard(ctx)

        return super(MrpWorkorder, self).end_all()

    def button_pending(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if not ctx.get('ignore_backdate_wizard_call', False) and not manual_validate_date_time and self.env.user.has_group('to_backdate.group_backdate'):
            ctx.update({'default_source_action': 'button_pending'})
            return self._prepare_backdate_wizard(ctx)
        return super(MrpWorkorder, self).button_pending()

    def button_unblock(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if not ctx.get('ignore_backdate_wizard_call', False) and not manual_validate_date_time and self.env.user.has_group('to_backdate.group_backdate') and not len(self) > 1:
            ctx.update({'default_source_action': 'button_unblock'})
            return self._prepare_backdate_wizard(ctx)
        return super(MrpWorkorder, self).button_unblock()

    def button_done(self):
        ctx = dict(self._context or {})
        manual_validate_date_time = ctx.get('manual_validate_date_time', False)
        if not ctx.get('ignore_backdate_wizard_call', False) and not manual_validate_date_time and self.env.user.has_group('to_backdate.group_backdate') and not len(self) > 1:
            ctx.update({'default_source_action': 'button_done'})
            return self._prepare_backdate_wizard(ctx)

        res = super(MrpWorkorder, self).button_done()
        if manual_validate_date_time:
            done_wo_ids = self.filtered(lambda wo: wo.state == 'done')
            if done_wo_ids:
                done_wo_ids.write({'date_finished': manual_validate_date_time})
        return res
