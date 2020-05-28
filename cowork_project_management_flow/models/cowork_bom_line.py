# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_bom_line(models.Model):
    _name = "cowork.bom.line"
    _description = "物料行"
    

    preliminary_scheme_id = fields.Many2one(comodel_name="cowork.scheme.preliminary", ondelete="cascade", string="项目初步方案")
