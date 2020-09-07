# -*- coding: utf-8 -*-
from odoo import http

# class Account.move.template(http.Controller):
#     @http.route('/account.move.template/account.move.template/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account.move.template/account.move.template/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account.move.template.listing', {
#             'root': '/account.move.template/account.move.template',
#             'objects': http.request.env['account.move.template.account.move.template'].search([]),
#         })

#     @http.route('/account.move.template/account.move.template/objects/<model("account.move.template.account.move.template"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account.move.template.object', {
#             'object': obj
#         })