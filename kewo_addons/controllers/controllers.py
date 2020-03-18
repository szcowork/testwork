# -*- coding: utf-8 -*-
from odoo import http

# class KewoAddons(http.Controller):
#     @http.route('/kewo_addons/kewo_addons/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kewo_addons/kewo_addons/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kewo_addons.listing', {
#             'root': '/kewo_addons/kewo_addons',
#             'objects': http.request.env['kewo_addons.kewo_addons'].search([]),
#         })

#     @http.route('/kewo_addons/kewo_addons/objects/<model("kewo_addons.kewo_addons"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kewo_addons.object', {
#             'object': obj
#         })