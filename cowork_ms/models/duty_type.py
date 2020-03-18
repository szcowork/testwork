# -*- coding: utf-8 -*-

from odoo import models, fields, api


class duty_type(models.Model):
    _name = "duty.type"
    _description = "请假类型"


    name = fields.Char(required=True, string="请假类型名称")
