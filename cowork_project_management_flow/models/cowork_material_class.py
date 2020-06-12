# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_material_class(models.Model):
    _name = "cowork.material.class"
    _description = "物料分类"
    

    name = fields.Char(required=True, string="名称")
    categ_id = fields.Many2one(comodel_name="cowork.material.category", required=True, string="项目")

    @api.multi
    def name_get(self):
        return [(record.id, "%s%s" % (record.categ_id.name + " \\ " if record.categ_id else "", record.name)) for record in self]