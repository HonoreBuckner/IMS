# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare

from odoo.exceptions import UserError

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    state = fields.Selection(selection_add=[('Validation', 'Validation')])
    steps = fields.Selection([('first_step', 'Etape 1'), ('second_step','Etape 2'), ('third_step', 'Etape 3')],string="Etape" ,default="first_step")
    is_refused = fields.Boolean("Refusé")
    
    @api.multi
    def first_validation(self):
        self.write({'state': 'to approve', 'steps': 'second_step'})
        return {}
#send mail to all users of the second group 
    @api.multi
    def second_validation(self):
        self.write({'state': 'to approve', 'steps': 'third_step'})
        
# send mail to all users of the third group
    def third_validation(self):
        self.button_approve()
        
       
        
        

          
#send mail to all users of the third group 

    @api.multi
    def refuse_purchase(self, reason):
        self.write({'is_refused': True})

