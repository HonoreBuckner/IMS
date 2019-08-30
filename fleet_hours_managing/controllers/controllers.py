# -*- coding: utf-8 -*-
from odoo import http

# class FleetHoursManaging(http.Controller):
#     @http.route('/fleet_hours_managing/fleet_hours_managing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fleet_hours_managing/fleet_hours_managing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fleet_hours_managing.listing', {
#             'root': '/fleet_hours_managing/fleet_hours_managing',
#             'objects': http.request.env['fleet_hours_managing.fleet_hours_managing'].search([]),
#         })

#     @http.route('/fleet_hours_managing/fleet_hours_managing/objects/<model("fleet_hours_managing.fleet_hours_managing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fleet_hours_managing.object', {
#             'object': obj
#         })