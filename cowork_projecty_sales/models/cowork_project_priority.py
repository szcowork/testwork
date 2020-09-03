# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_project_priority(models.Model):
    _name = "cowork.project.priority"
    _description = "项目优先级"
    

    name = fields.Char(string="名称")
