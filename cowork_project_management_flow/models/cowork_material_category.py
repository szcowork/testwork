# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_material_category(models.Model):
    _name = "cowork.material.category"
    _description = "物料项目"
    

    name = fields.Char(required=True, string="名称")
