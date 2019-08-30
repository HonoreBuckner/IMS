from odoo import api, fields, models, _
from odoo.exceptions import UserError

from dateutil.relativedelta import relativedelta

										
class FleetVehicleCost(models.Model):
    _inherit = "fleet.vehicle.cost"

    counter_time = fields.Float(compute="_get_horaire", inverse='_set_horaire',string="Temps du compteur Horaire")
    counter_time_id = fields.Many2one('fleet_hours_managing.horaire', 'Horaire', help='Compteur horaire au moment du service')
    meter_reading_date = fields.Date(string="Date du relèvement")
    def _get_horaire(self):
        for record in self:
            if record.counter_time_id:
                record.counter_time = record.counter_time_id.value

    def _set_horaire(self):
        for record in self:
            if not record.counter_time:
                raise UserError(_('Emptying the horaire value of a vehicle is not allowed.'))
            counter_time = self.env['fleet_hours_managing.horaire'].create({
                'value': record.counter_time,
                'date': record.date or fields.Date.context_today(record),
                'vehicle_id': record.vehicle_id.id
            })
            self.counter_time_id = counter_time
 
class FleetVehicleLogServices(models.Model):
    _inherit="fleet.vehicle.log.services"
	
    name = fields.Char(compute='_compute_vehicle_log_name', store=True)	
    lot_services_id = fields.Many2one('fleet_hours_managing.lotservice', string="Lot de Service")
    services = fields.Many2many('fleet.service.type', 'services_log_service_rel','service_type_id','log_id',string="Services")
    serial_number = fields.Char(related="vehicle_id.serial_number")
    parc_number = fields.Char(related="vehicle_id.parc_number")
    picking_ids = fields.One2many('stock.picking','service_id', string="Sorties de stocks")
    services_date = fields.Date(string="Date du service")
    service_type = fields.Selection([('curative','Curative'),('preventive','Préventive')],string="Types d'intervention", index=True)
    state = fields.Selection([('draft','Brouillon'),('done','Effectuer')],string="Status",default="draft")
	
    @api.depends('vehicle_id', 'date', 'lot_services_id')
    def _compute_vehicle_log_name(self):
        for record in self:
            name = str(record.vehicle_id.name) + ' / ' + str(record.lot_services_id.time_needed)
            if not name:
                name = ' /' + str(record.lot_services_id.time_needed)
            record.name = name	
	
    @api.onchange('lot_services_id')
    def _onchange_lot_services_id(self):
        if not self.lot_services_id:
            return 
        self.services = [(6,0,self.lot_services_id.service_type_ids.ids)]
            
    @api.multi
    def action_validate(self):
        for record in self:
            record.counter_time_id.validate()
            record.write({'state':'done'})
            record.vehicle_id.services_reminder()
	
    @api.multi
    def action_cancel(self):
        for record in self:
		#delete associate records like horaire object and odometer
            record.counter_time_id.unlink()
            record.odometer_id.unlink()
            record.write({'state':'draft'})
    
	
	



class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'
	
    contract_name = fields.Char(string="Nom du contrat", required=True)
	
    @api.depends('vehicle_id', 'cost_subtype_id', 'date')
    def _compute_contract_name(self):
        for record in self:
            record.name = record.contract_name + '/ ' + record.vehicle_id.name
            