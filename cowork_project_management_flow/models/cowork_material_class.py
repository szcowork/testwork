# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_material_class(models.Model):
    _name = "cowork.material.class"
    _description = "物料分类"
    

    name = fields.Char(required=True, string="名称")
    categ_id = fields.Many2one(comodel_name="cowork.material.category", required=True, string="项目")
