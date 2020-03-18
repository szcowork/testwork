# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import logging
_logger = logging.getLogger(__name__)
class overtime_appoval(models.Model):
    _name = "overtime.appoval"
    _description = "加班申请"
    _inherit = "einfo.approval"

    @api.model
    def default_get(self, fields):
        res = super(overtime_appoval, self).default_get(fields)
        res.update({
        'name': time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        })
        return res

    name = fields.Char(required=True, string="单号")

    reason = fields.Text(required=True, string="事由")
    start_time = fields.Datetime(required=True, string="开始时间")
    end_time = fields.Datetime(required=True, string="结束时间")
    time_last = fields.Float(string="持续时间")
    overtime_type = fields.Many2one(comodel_name="overtime.type", required=True, string="加班类型")
