from odoo import api, fields, models, tools, SUPERUSER_ID, _

class Partner(models.Model):
    _inherit = "res.partner"

    # _sql_constraints = [
    #     ('ref_uniq', 'unique (ref)',
    #      'The Reference must be unique!')
    # ]