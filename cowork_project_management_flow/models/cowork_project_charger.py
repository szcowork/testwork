# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_project_charger(models.Model):
    _name = "cowork.project.charger"
    _description = "项目负责人"
    

    apply_id = fields.Many2one(comodel_name="cowork.project.apply", ondelete="cascade", string="立项申请")
    job_id = fields.Many2one(comodel_name="hr.job", string="岗位")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="员工")
