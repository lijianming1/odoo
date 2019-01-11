# -*- coding: utf-8 -*-
from odoo import http

# class TjMachinesStock(http.Controller):
#     @http.route('/tj_machines_stock/tj_machines_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tj_machines_stock/tj_machines_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tj_machines_stock.listing', {
#             'root': '/tj_machines_stock/tj_machines_stock',
#             'objects': http.request.env['tj_machines_stock.tj_machines_stock'].search([]),
#         })

#     @http.route('/tj_machines_stock/tj_machines_stock/objects/<model("tj_machines_stock.tj_machines_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tj_machines_stock.object', {
#             'object': obj
#         })