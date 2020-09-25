# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



from werkzeug.urls import url_encode


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shipment_packing = fields.Selection(
        [('delivery_order', 'Bulk Shipment'), ('invoice', 'Container')],
        'Shipment Packing', default='')


