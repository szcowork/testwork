# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

class hire_approval(models.Model):
    _name = "hire.approval"
    _description = "招聘申请"
    _inherit = "einfo.approval"



    posi = fields.Many2one(comodel_name="hr.job", required=True, string="招聘岗位")
    belong = fields.Many2one(comodel_name="hr.job", required=True, string="所属岗位")
    count = fields.Integer(required=True, string="招聘人数")
    reason = fields.Text(required=True, string="原因")
    work = fields.Text(required=True, string="岗位职责")
    request = fields.Text(required=True, string="岗位要求")
    # applier = fields.Many2one(comodel_name="hr.employee", required=True, string="申请人")
