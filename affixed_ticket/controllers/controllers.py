# -*- coding: utf-8 -*-
from odoo import http

# class AffixedTicket(http.Controller):
#     @http.route('/affixed_ticket/affixed_ticket/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/affixed_ticket/affixed_ticket/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('affixed_ticket.listing', {
#             'root': '/affixed_ticket/affixed_ticket',
#             'objects': http.request.env['affixed_ticket.affixed_ticket'].search([]),
#         })

#     @http.route('/affixed_ticket/affixed_ticket/objects/<model("affixed_ticket.affixed_ticket"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('affixed_ticket.object', {
#             'object': obj
#         })