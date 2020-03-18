# -*- coding: utf-8 -*-

from odoo import models, fields, api

import time

class duty_approval(models.Model):
    _name = "duty.approval"
    _description = "请假申请"
    _inherit = "einfo.approval"

    @api.model
    def default_get(self, fields):
        res = super(duty_approval, self).default_get(fields)
        res.update({
        'name': time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        })
        return res

    name = fields.Char(required=True, string="单号")
    # eply = fields.Many2one(comodel_name="hr.employee", required=True, string="员工")
    # posi = fields.Many2one('hr.job',related="eply.job_id", string="岗位")
    dtype = fields.Many2one(comodel_name="duty.type", required=True, string="请假类型")
    reason = fields.Text(required=True, string="事由")
    start_date = fields.Date(required=True, string="开始日期")
    end_date = fields.Date(required=True, string="结束日期")
    day_last = fields.Integer(string="持续时间")
