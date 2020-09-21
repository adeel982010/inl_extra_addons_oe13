from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def action_cancel(self):
        quant_obj = self.env['stock.quant']
        account_move_obj = self.env['account.move']
        dp_obj = self.env['decimal.precision']
        for inv_adjustment in self:
            if inv_adjustment.company_id.cancel_done_inv:
                for move in inv_adjustment.move_ids:
                    if move.state == 'cancel':
                        continue
                    if move.state == "done" and move.product_id.type == "product":
                        for move_line in move.move_line_ids:
                            quantity = move_line.product_uom_id._compute_quantity(move_line.qty_done,
                                                                                  move_line.product_id.uom_id)
                            quant_obj._update_available_quantity(move_line.product_id, move_line.location_id, quantity,
                                                                 move_line.lot_id)
                            quant_obj._update_available_quantity(move_line.product_id, move_line.location_dest_id,
                                                                 quantity * -1, move_line.lot_id)
                    elif move.procure_method == 'make_to_order' and not move.move_orig_ids:
                        move.state = 'waiting'
                    elif move.move_orig_ids and not all(
                            orig.state in ('done', 'cancel') for orig in move.move_orig_ids):
                        move.state = 'waiting'
                    else:
                        move.state = 'confirmed'
                    siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
                    for ml in move.move_line_ids:
                        precision = dp_obj.precision_get('Product Unit of Measure')
                        # Unlinking a move line should unreserve.
                        if ml.product_id.type == 'product' and not ml.location_id.should_bypass_reservation() and not float_is_zero(
                                ml.product_qty, precision_digits=precision):
                            try:
                                quant_obj._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty,
                                                                    lot_id=ml.lot_id, package_id=ml.package_id,
                                                                    owner_id=ml.owner_id, strict=True)
                            except UserError:
                                if ml.lot_id:
                                    quant_obj._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty,
                                                                        lot_id=False, package_id=ml.package_id,
                                                                        owner_id=ml.owner_id, strict=True)

                        moves = ml.mapped('move_id')

                        if moves:
                            moves._recompute_state()
                        ml.state = 'draft'
                        ml.unlink()
                    if move.propagate_cancel:
                        if all(state == 'cancel' for state in siblings_states):
                            move.move_dest_ids._action_cancel()
                    else:
                        if all(state in ('done', 'cancel') for state in siblings_states):
                            move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                        move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
                    move.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
                    valuation = move.stock_valuation_layer_ids
                    valuation and valuation.sudo().unlink()
                    account_moves = account_move_obj.search([('stock_move_id', '=', move.id)])
                    if account_moves:
                        for account_move in account_moves:
                            account_move.button_cancel()
                            account_move.with_context(force_delete=True).unlink()
                inv_adjustment.write({'state': 'cancel'})
        return True
