from reportlab.graphics.transform import inverse

from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import ValidationError

from odoo.exceptions import ValidationError
from odoo.tools.populate import compute


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offers'

    price = fields.Float(string="Price")
    status = fields.Selection(
        [('accepted','Accepted'), ('refused','Refused')],
        string="Status")

    partner_id = fields.Many2one('res.partner', string="Customer")
    property_id = fields.Many2one('estate.property', string="Property")
    validity = fields.Integer("Validity")
    deadline = fields.Date("Deadline", compute='_compute_deadline', inverse='_inverse_deadline')
    @api.model
    def _set_create_date(self):
        return fields.Date.today()

    #_sql_constraints = [
       # ('check_validity', 'check(validity > 0)', 'Deadline cannot be before creation date')
    #]

    @api.constrains('validity')
    def _check_validity(self):
        for rec in self:
            if rec.deadline <= rec.creation_date:
                raise ValidationError("Deadline cannot be before creation date")



    creation_date = fields.Date("Creation Date", default=_set_create_date)

    @api.depends('validity', 'creation_date')
    def _compute_deadline(self):
        for rec in self:
            if rec.creation_date and rec.validity:
                rec.deadline = rec.creation_date + timedelta(days=rec.validity)
            else:
                rec.deadline = False
    def _inverse_deadline(self):
        for rec in self:
            rec.validity = (rec.deadline - rec.creation_date).days