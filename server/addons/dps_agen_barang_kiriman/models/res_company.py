from odoo import models, fields, api

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    agen_id = fields.Many2one(
        'dps.agen.barkir',
        string='Agen Terkait'
    )