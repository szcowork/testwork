# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_apply_id = fields.Many2one(comodel_name="sale.apply", string="项目式销售")

class ps_purchase_requisition(models.Model):
    _inherit = "ps.purchase.requisition"

    sale_apply_id = fields.Many2one(comodel_name="sale.apply", string="项目式销售")