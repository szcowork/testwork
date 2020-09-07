# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

class hire_check(models.Model):
    _name = "hire.check"
    _description = "面试评价单"
    _inherit = "einfo.approval"
    
    @api.model
    def default_get(self, fields):
        res = super(hire_check, self).default_get(fields)
        res.update({
        'name': time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        })
        return res

    name = fields.Char(required=True, string="单号")
    interviewer = fields.Many2one(comodel_name="hr.employee", required=True, string="面试官")
    interviewer_department = fields.Many2one( related="interviewer.department_id", string="面试官部门")
    interviewer_posi = fields.Many2one( related="interviewer.job_id", string="面试官岗位")
    application_posi = fields.Many2one(comodel_name="hr.job", required=True, string="应聘岗位")
    applicant = fields.Char(required=True, string="应聘人姓名")
    is_quit = fields.Boolean(required=True, string="是否离职")
    arrival_time = fields.Date(required=True, string="预计到岗时间")
    salary = fields.Float(required=True, string="薪资要求（税前）")
    evaluate = fields.Binary(required=True, string="面试评价表")
    content = fields.Text(string="备注")
