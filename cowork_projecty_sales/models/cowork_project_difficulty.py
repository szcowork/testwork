# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_project_difficulty(models.Model):
    _name = "cowork.project.difficulty"
    _description = "项目难度"
    

    name = fields.Char(string="名称")
