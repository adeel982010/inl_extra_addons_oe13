import logging

from odoo import api, fields, models, tools, _, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # _sql_constraints = [
    #     ('default_code_uniq', 'unique (default_code)',
    #      'The Product Code of the product must be unique!')
    # ]

    default_code = fields.Char(
        'Product Code', compute='_compute_default_code',
        inverse='_set_default_code', store=True, required=True)