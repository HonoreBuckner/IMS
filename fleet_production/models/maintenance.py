from odoo import fields, models, api

class HrMaintenancePrograms(models.Model):
    _name = 'maintenance.programs'


    name = fields.Char('Nom de la Maintenance')
    equipment_ids = fields.Many2many('maintenance.equipment', string="Equipements du programmes")
    maintenance_hours = fields.Float("Heures De Maintenance")



class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule du parc')

    _sql_constraints = [
        ('vehicle_uniq', 'unique (vehicle_id)', "An Equipment is already link to this vehicle"),
    ]


class HrMaintenance(models.Model):
    _inherit = 'maintenance.request'

    vehicle_id = fields.Many2one(related='equipment_id.vehicle_id')
    odometer = fields.Float('Compteur horaire à la maintenance')

    def _update_vehicle_info(self):
        pass





