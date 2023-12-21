from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    start_date = fields.Date("Date début")
    end_date = fields.Date("Date fin")

    @api.depends('start_date', 'end_date')
    def compute_customer_period_sale(self):
        if not self.end_date and self.start_date:
            raise ValidationError("Veuillez Saisir la date de début et de fin")
        if self.start_date > self.end_date:
            raise UserError("La date de début doit être avant la date de fin")
        production_logs = self.env['fleet.production'].search([('customer_id', '=', self.partner_id.id),
            ('date', '>=', self.start_date), ('date', '<=', self.end_date)])
