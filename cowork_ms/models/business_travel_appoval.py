# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

class business_travel_appoval(models.Model):
    _name = "business.travel.appoval"
    _description = "出差申请"
    _inherit = "einfo.approval"

    @api.model
    def default_get(self, fields):
        res = super(business_travel_appoval, self).default_get(fields)
        res.update({
        'name': time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        })
        return res


    name = fields.Char(required=True, string="单号")
    # eply = fields.Many2one(comodel_name="hr.employee", required=True, string="员工")
    # posi = fields.Many2one('hr.job',required=True, related="eply.job_id", string="岗位")
    reason = fields.Text(required=True, string="出差事由")
    place = fields.Char(required=True, string="出差地点")
    start_time = fields.Datetime(required=True, string="开始时间")
    end_time = fields.Datetime(required=True, string="结束时间")
