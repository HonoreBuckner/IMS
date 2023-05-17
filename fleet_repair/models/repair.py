
from odoo import api, models, fields


class Repair(models.Model):
    _inherit = 'repair.order'

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle to repair", required=True)
    location_id = fields.Many2one(related="vehicle_id.location_id", string="vehicle location")
    product_id =fields.Many2one('product.product', string='Product to Repair', readonly=True, required=False)

class RepairLine(models.Model):
    _inherit = 'repair.line'

    @api.depends('type')
    def _compute_location_id(self):
        for line in self:
            if not line.type:
                line.location_id = False
                line.location_dest_id = False
            elif line.type == 'add':
                args = line.repair_id.company_id and [('company_id', '=', line.repair_id.company_id.id)] or []
                warehouse = line.env['stock.warehouse'].search(args, limit=1)
                line.location_id = warehouse.lot_stock_id
                line.location_dest_id = line.repair_id.location_id
            else:
                line.location_id = line.repair_id.location_id
                line.location_dest_id = line.env['stock.location'].search(
                    [('scrap_location', '=', True), ('company_id', 'in', [line.repair_id.company_id.id, False])],
                    limit=1).id
