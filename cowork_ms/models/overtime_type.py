# -*- coding: utf-8 -*-

from odoo import models, fields, api


class overtime_type(models.Model):
    _name = "overtime.type"
    _description = "加班类型"


    name = fields.Char(required=True, string="名称")
