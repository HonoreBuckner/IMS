from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
from datetime import timedelta

class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"


    time_counter = fields.Float(compute='_get_time_counter', inverse='_set_time_counter',string="Dernier Temps horaire",help="dernier saisie du compteur horaire")
    components_ids = fields.One2many('maintenance.equipment', 'vehicle_id', string='Les composants')
    previous_service_date = fields.Date(string='Date du precedent service', compute="_compute_service_fields")
    next_service_date = fields.Date(string='date du service suivant', compute="_compute_service_fields")
    next_service_time = fields.Integer(string='Temps du service suivant', compute="_compute_service_fields")
    previous_service_time = fields.Integer(string='Temps du service precedent', compute="_compute_service_fields")
    time_before_next_service = fields.Float(string='Temps avant prochain service', compute="_compute_service_fields")
    last_service_odometer = fields.Float(string="Kilometrage au dernier service", compute="_compute_service_fields")
    horaire_count = fields.Integer(compute='_compute_horaire_count', string='Horaires')
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='Equipements')
    serial_number = fields.Char(string="Numero de serie")
    parc_number = fields.Char(string="Numero de parc")
    log_components = fields.One2many('fleet.vehicle.component.log', 'vehicle_id', string='Suivi des composants')

    
    @api.multi
    def services_reminder(self):
        if self.time_before_next_service < 48:
            # model_id = self.env['ir.model'].search(['model','=','fleet.vehicle'], limit=1).id
            # activity_type_id = self.env['mail.activity.type'].search(['name','=','intervention'], limit=1).id
            activity = {
				'activity_type_id': 1,
				'res_id':self.id,
				'res_model_id':168,
				'summary':'Services ' + str(self.next_service_time) + 'Heures' ,
				'note':"La maintenance preventive du vehicule %s approche" % self.name,
				'date_deadline':fields.Date.today() + timedelta(days=2),
				'automated':True,
				}
            self.env['mail.activity'].create(activity)
                

	
    @api.multi
    def _compute_service_fields(self):
        all_services = self.env['fleet_hours_managing.lotservice']
        for vehicle in self:
            last_services = self.env['fleet.vehicle.log.services'].search([('vehicle_id', '=', vehicle.id)], limit=1, order='date desc')
            if last_services and last_services.date:
                vehicle.previous_service_date = last_services.date
                vehicle.previous_service_time = last_services.lot_services_id.time_needed
                vehicle.next_service_date = last_services.date + timedelta(days=1)
                
                vehicle.next_service_time = 250*(int(vehicle.time_counter/250)) + 250
                vehicle.time_before_next_service = vehicle.next_service_time - vehicle.time_counter
    @api.multi
    def _get_time_counter(self):
        FleetVehicalCounter = self.env['fleet_hours_managing.horaire']
        for record in self:
            vehicle_time_counter = FleetVehicalCounter.search([('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if vehicle_time_counter:
                record.time_counter = vehicle_time_counter.value
            else:
                record.time_counter = 0

    def _set_time_counter(self):
        for record in self:
            if record.time_counter:
                date = fields.Date.context_today(record)
                data = {'value': record.time_counter, 'date': date, 'vehicle_id': record.id}
                self.env['fleet_hours_managing.horaire'].create(data)
				

    @api.multi
    def _compute_horaire_count(self):
        Horaire = self.env['fleet_hours_managing.horaire']
        for record in self:
            record.horaire_count = Horaire.search_count([('vehicle_id', '=', record.id)])

    @api.multi
    def _compute_equipment_count(self):
        Equipement = self.env['maintenance.equipment']
        for record in self:
            record.equipment_count = Equipement.search_count([('vehicle_id', '=', record.id)])
			
			
    _sql_constraints = [('fleet_serial_number_unique', 'unique(serial_number)', 'Serial number already exists')]
    _sql_constraints = [('fleet_parc_number_unique', 'unique(parc_number)', 'Parc number already exists')]


class FleetVehicleHoraire(models.Model):
    _name = 'fleet_hours_managing.horaire'
    _description = 'horaire log for a vehicle'
    _order = 'date desc'

    name = fields.Char(compute='_compute_vehicle_log_name', store=True)
    date = fields.Date(default=fields.Date.context_today, track_visibility='always', required=True)
    value = fields.Float('Valeur horaire', group_operator="max", track_visibility='always', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True, track_visibility='onchange')
    driver_id = fields.Many2one(related="vehicle_id.driver_id", string="Driver", readonly=False)
    note = fields.Char(string="note")
    delta_time_inf = fields.Float(compute="_compute_delta_time")
	
	
    def _compute_delta_time(self):
        FleetVehicalCounter = self.env['fleet_hours_managing.horaire']
        for horaire in self:
            vehicle_counter_inf = FleetVehicalCounter.search([('vehicle_id', '=', horaire.vehicle_id.id),('date','<',horaire.date)], limit=1, order='date desc')
            if vehicle_counter_inf.value:
                horaire.delta_time_inf = horaire.value - vehicle_counter_inf.value
            else:
                horaire.delta_time_inf = 0.0			

    @api.depends('vehicle_id', 'date')
    def _compute_vehicle_log_name(self):
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = str(record.date)
            elif record.date:
                name += ' / ' + str(record.date)
            record.name = name
 
    @api.model
    def create(self, vals):
        FleetVehicalCounter = self.env['fleet_hours_managing.horaire']
        vehicle_counter_sup = FleetVehicalCounter.search([('vehicle_id', '=', vals['vehicle_id']),('date','>',vals['date'])], limit=1, order='date asc')
        vehicle_counter_inf = FleetVehicalCounter.search([('vehicle_id', '=', vals['vehicle_id']),('date','<',vals['date'])], limit=1, order='date desc')
        if len(FleetVehicalCounter) > 0 and not (vehicle_counter_inf.value or vehicle_counter_sup.value):
            raise ValidationError(_("nombre de releve :%s et inf :%s et sup:%s") % (len(FleetVehicalCounter),vehicle_counter_inf.value,vehicle_counter_sup.value) )
        if 'value' in vals :
            if vehicle_counter_sup and vehicle_counter_sup.value:
                if vehicle_counter_sup.value < vals['value']:
                    raise ValidationError(_("Un compteur horaire moins recent date:%s; horaire:%s ne peut pas superieur à un de plus recent date:%s; horaire:%s") %(vals['date'],vals['value'],vehicle_counter_sup.date,vehicle_counter_sup.value))
                elif vehicle_counter_sup.value < (vals['value'] + 0.5):
                    raise ValidationError(_("Le temps minimum de travail des vehicules est de 30 minutes. temps précedent :%s, temps suivant:%s ") %(vals['value'],vehicle_counter_sup.value))
            if vehicle_counter_inf and vehicle_counter_inf.value:
                if vehicle_counter_inf.value > vals['value']:
                    raise ValidationError(_("Un compteur horaire moins recent date:%s; horaire:%s ne peut pas être superieur à un de plus recent date:%s; horaire:%s") %(vehicle_counter_inf.date,vehicle_counter_inf.value,vals['date'],vals['value']))
                elif vehicle_counter_inf.value > (vals['value'] - 0.5):
                    raise ValidationError(_("Le temps minimum de travail des vehicules est de 30 minutes. temps précedent :%s, temps suivant:%s ") %(vehicle_counter_inf.value,vals['value']))
        else:
            raise ValidationError(_("Programming error:"))
        vals['note'] = str(vehicle_counter_sup.date)+"::" + str(vehicle_counter_sup.value) + str(vehicle_counter_inf.date) + str(vehicle_counter_inf.value)
        vals['note'] += "vals value:%s, date: %s, vehicle:%s" % (str(vals['value']),str(vals['date']),str(vals['vehicle_id']))
        res = super(FleetVehicleHoraire, self).create(vals)

        return res
		

    @api.multi
    def validate(self):
        FleetVehicalCounter = self.env['fleet_hours_managing.horaire']
        vehicle_counter_sup = FleetVehicalCounter.search([('vehicle_id', '=', self.vehicle_id.id),('date','>',self.date)], limit=1, order='date asc')
        vehicle_counter_inf = FleetVehicalCounter.search([('vehicle_id', '=', self.vehicle_id.id),('date','<',self.date)], limit=1, order='date desc')
        delta_inf = self.value - vehicle_counter_inf.value if vehicle_counter_inf.value else self.value
        if not vehicle_counter_sup:
            for component in self.vehicle_id.components_ids:
                component.add_time(delta_inf)
	
    @api.multi
    def write(self, vals):
        res = super(FleetVehicleHoraire, self).write(vals)

        FleetVehicalCounter = self.env['fleet_hours_managing.horaire']
        if 'date' in vals or 'vehicle_id' in vals:
            raise ValidationError(_("La date ni le véhicule ne peut être changé après création du relevé. Supprimer le relèvement ou Mettez l'intervention en brouillon "))

        vehicle_counter_sup = FleetVehicalCounter.search([('vehicle_id', '=', self.vehicle_id.id),('date','>',self.date)], limit=1, order='date asc')
        vehicle_counter_inf = FleetVehicalCounter.search([('vehicle_id', '=', self.vehicle_id.id),('date','<',self.date)], limit=1, order='date desc')
        if len(FleetVehicalCounter) > 0 and not (vehicle_counter_inf.value or vehicle_counter_sup.value):
            raise ValidationError(_("nombre de relévé :%s et inf :%s et sup:%s") % (len(FleetVehicalCounter),vehicle_counter_inf.value,vehicle_counter_sup.value) )
        if 'value' in vals:
            if vals['value'] < 0.5:
                raise ValidationError(_("La valeur du compteur ne peut être inferieur à 30 minutes soit 0.5 heures"))
            if vehicle_counter_sup and vehicle_counter_sup.value:
                if vehicle_counter_sup.value < vals['value']:
                    raise ValidationError(_("Un compteur horaire moins recent %s:%s ne peut pas superieur à un de plus recent %s:%s") %(vals['date'],vals['value'],vehicle_counter_sup.date,vehicle_counter_sup.value))
                elif vehicle_counter_sup.value < (vals['value'] + 0.5):
                    raise ValidationError(_("Le temps minimum de travail des vehicules est de 30 minutes. temps précedent :%s, temps suivant:%s ") %(vals['value'],vehicle_counter_sup.value))
            if vehicle_counter_inf and vehicle_counter_inf.value:
                if vehicle_counter_inf.value > vals['value']:
                    raise ValidationError(_("Un compteur horaire moins recent %s:%s ne peut pas superieur à un de plus recent %s:%s") %(vehicle_counter_inf.date,vehicle_counter_inf.value,vals['date'],vals['value']))
                elif vehicle_counter_inf.value > (vals['value'] - 0.5):
                    raise ValidationError(_("Le temps minimum de travail des vehicules est de 30 minutes. temps précedent :%s, temps suivant:%s ") %(vehicle_counter_inf.value,vals['value']))
        
        vals['note'] = str(vehicle_counter_sup.date)+"::" + str(vehicle_counter_sup.value) + str(vehicle_counter_inf.date) + str(vehicle_counter_inf.value)
        vals['note'] += "vals value:%s, date: %s, vehicle:%s, ancien value:%s" % (str(vals['value']),str(vals['date']),str(vals['vehicle_id']),str(self.value))
        return res
		
    @api.multi
    def unlink(self):
        for record in self:
            for component in record.vehicle_id.components_ids:
                component.add_time(-record.delta_time_inf)
        return super(FleetVehicleHoraire, self).unlink()
	

class Composant(models.Model):
    _inherit = 'maintenance.equipment'

    expected_life = fields.Integer(string='durée de vie')
    time_of_use = fields.Float(string="temps d'utilisation", default=0.0)
    alert_time = fields.Integer(string="Temps pour alerter")
    initial_time_of_component = fields.Float(help="Temps du composant lors de l'association au vehicule", default=0.0)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicule")
    #Add vehicle change log, to follow components changing like driver log for vehicle
    log_vehicles = fields.One2many('fleet.vehicle.component.log', 'component_id', string="Historique des vehicules")
    active = fields.Boolean(string="En activité", default=False)
    			
    @api.depends('vehicle_id')
    def _vehicle_onchange(self):
        if self.vehicle_id:
            active =True
        else:
            active = False


    @api.multi
    def add_time(self, time):
        if time:
            self.time_of_use += time

    @api.model
    def create(self, vals):
        res = super(Composant, self).create(vals)
        if 'vehicle_id' in vals:
            active = True
        if 'initial_time_of_component' in vals:
            self.time_of_use = vals['initial_time_of_component']
        else:
            self.time_of_use = 0.0
        if 'expected_life' in vals:
            self.alert_time = vals['alert_time'] if 'alert_time' in vals else 5*vals['expected_life']/100
        return res			

class FleetServiceType(models.Model):
    _inherit = "fleet.service.type"
	
    need_stock = fields.Boolean(string="necessite une sortie de stock")
    component_ids = fields.Many2many('maintenance.equipment','service_type_equipment_rel','service_type_id','equipment_id',string="Composants nécessaire")


class LotService(models.Model):
    _name = 'fleet_hours_managing.lotservice'
    _description = 'Lot de service'
    _order = 'time_needed, id'

    name = fields.Char(string="Nom du Lot")
    time_needed = fields.Integer(string="Temps d'application")
    service_type_ids = fields.Many2many('fleet.service.type', 'fleet_hours_managing_lotservices_service_type_rel', 'lotservice_id',
                                        'service_type_id', string="Les services du lot")
			
class FleetVehicleComponentLog(models.Model):
    _name = "fleet.vehicle.component.log"
    _description = "Historique des vehicules du composants"
    _order = "date_start"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", required=True)
    component_id = fields.Many2one('maintenance.equipment', string="equipement", required=True)
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
