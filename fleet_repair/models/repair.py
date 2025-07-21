
from odoo import api, models, fields


class Repair(models.Model):
    _inherit = 'repair.order'

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle to repair", required=True)
    location_id = fields.Many2one(related="vehicle_id.location_id", string="vehicle location")
    product_id =fields.Many2one('product.product', string='Product to Repair', readonly=True, required=False)
