# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrExpenseRefuseWizard(models.TransientModel):
    
    _name = "purchase.refuse.wizard"
    _description = "Purchase Refuse Reason Wizard"

    reason = fields.Char(string='Reason', required=True)
    purchase_id = fields.Many2one('purchase.order', string="Commande Achat")


    @api.multi
    def purchase_refuse_reason(self):
        self.ensure_one()
        if self.purchase_id:
            self.purchase_id.refuse_purchase(self.reason)
        
        return {'type': 'ir.actions.act_window_close'}