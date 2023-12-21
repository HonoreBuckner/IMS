from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class FleetProduction(models.Model):
    _name = 'fleet.production'
    _description = 'Journal de Production'



    vehicle_id = fields.Many2one('fleet.vehicle', string='Véhicule/Engin', required=True)
    operator = fields.Many2one('res.users', string='Opérateur', required=True, default=lambda self: self.env.user)
    date = fields.Date(string='Date', required=True)
    morning_hours = fields.Float(string='Heures du Matin')
    evening_hours = fields.Float(string='Heures du Soir')
    total_day_hours = fields.Float("Total du Jour", compute='_compute_total_day_work')
    day_load = fields.Float("Quantité du Jour")
    object_loaded = fields.Char("Chargement")
    customer_id = fields.Many2one("res.partner", string="Client")
    state = fields.Selection([('draft', 'Saisi'), ('validated', 'Validé'), ('invoiced', 'Facturé')])
    sale_id = fields.Many2one("sale.order", string="Vente Associé")
    site = fields.Many2one('fleet.production.site', string="Site")
    load_required = fields.Boolean(related='site.load_require_site')
    partner_hours = fields.Float('Heures du Client')
    difference = fields.Float("Difference avec le client", compute='_compute_difference')



    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        if self.vehicle_id:
            if not self.vehicle_id.site:
                raise ValidationError("Le site actuel du véhicule n'est pas defini")
            self.site = self.vehicle_id.site

    @api.depends('partner_hours', 'morning_hours', 'evening_hours')
    def _compute_difference(self):
        for prod in self:
            if prod.partner_hours:
                prod.difference = prod.morning_hours + prod.evening_hours - prod.partner_hours

    @api.depends('morning_hours', 'evening_hours')
    def _compute_total_day_work(self):
        for prod in self:
            prod.total_day_hours = prod.morning_hours + prod.evening_hours

    def write(self, vals):
        if not self.total_day_hours:
            raise ValidationError('Renseignez les heures merci')
        if self.load_required and not self.day_load:
            raise ValidationError('Veuillez Renseigner la quantité chargée, elle est requise pour ce site')
        return super(FleetProduction, self).write(vals)

    def validate_production(self):
        for prod in self:
            if not (prod.morning_hours or prod.evening_hours or prod.day_load):
                raise UserError("Vous Devez saisir les heures ou la quantité chargée du jour")
            prod.write({'state':'validated'})
            prod.vehicle_id.write({'odometer': prod.vehicle_id.odometer + prod.vehicle_id.total_day_hours})


class FleetProductionSite(models.Model):
    _name = 'fleet.production.site'
    _description = "Site de Production"

    name = fields.Char('Nom du Site')
    customer_id = fields.Many2one('res.partner', string="Client du Site")
    load_require_site = fields.Boolean("Site Avec Chargement Requis")

