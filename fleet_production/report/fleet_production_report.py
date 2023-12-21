from odoo import fields, models, api


class FleetProductionReport(models.Model):
    _name = 'fleet.production.report'
    _description = 'Rapport de production'

    name = fields.Char()
