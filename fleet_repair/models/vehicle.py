from odoo import api, models, fields


class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    location_id = fields.Many2one("stock.location",string="vehicle stock location")
