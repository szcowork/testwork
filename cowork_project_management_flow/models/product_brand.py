# -*- coding: utf-8 -*-

from odoo import models, fields, api


class product_brand(models.Model):
    _name = "product.brand"
    _description = "品牌"
    

    name = fields.Char(string="名称")
