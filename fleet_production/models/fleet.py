from odoo import fields, models, api
from odoo.exceptions import UserError

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    hourly_rate = fields.Float(string='Taux horaire', required=True)
    work_logs = fields.One2many('fleet.production', 'vehicle_id', string='Historique des heures de travail')
    odometer = fields.Float(string='Compteur horaire', tracking=True)
    odometer_unit = fields.Selection(selection_add=[('hours', 'Heures')])
    scheduled_work_hours = fields.Float("Heures Prévues/jour")
    site = fields.Many2one("fleet.production.site", string="Site Actuel de Production")
    equipment_id = fields.Many2one('maintenance.equipment', string="Engins", compute='_create_equipment', store=True)
    last_maintenance_hours = fields.Float('Heures de la Dernière Maintenance', compute='compute_last_maintenance', store=True)
    next_maintenance_hours = fields.Float('Heures du prochain Maintenance', compute='compute_last_maintenance', store=True)

    def _create_equipment(self):
        for vehicle in self:
            if not self.env['maintenance.equipment'].search([('vehicle_id', '=', vehicle.id)]):
                equipment = self.env['maintenance.equipment'].create({
                    'name': str(vehicle.x_parc_number) + ':' + str(vehicle.name),
                    'model': vehicle.model_id.name,
                    'vehicle_id': vehicle.id
                })
                vehicle.equipment_id = equipment
            else:
                raise UserError("L'equipement associé existe déjà")

    @api.depends('equipment_id.maintenance_count')
    def compute_last_maintenance(self):
        for vehicle in self:
            last_maintenance_done = self.env['maintenance.request'].search([
                ('equipment_id', '=', vehicle.equipment_id.id),
                ('maintenance_type', '=', 'preventive')], order="close_date desc", limit=1)
            vehicle.last_maintenance_hours = last_maintenance_done.odometer

    @api.depends('odometer')
    def compute_next_maintenance(self):
        for vehicle in self:
            if vehicle.odometer and vehicle.last_maintenance_hours :
                vehicle.next_maintenance = vehicle.last_maintenance_hours + 250


