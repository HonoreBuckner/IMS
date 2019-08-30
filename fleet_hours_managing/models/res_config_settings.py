from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
	
    check_horaire_records = fields.Boolean(string="Vérification des relevés du compteur horaire",help="Les compteurs horaire de vront être croissant en date et en valeurs")

