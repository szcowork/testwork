# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class cowork_message(models.Model):
    _name = 'cowork.message'

    user_id = fields.Many2one("res.users",string="操作人")
    date = fields.Datetime(default=fields.Datetime.now(),string="时间")
    operate = fields.Text(string="操作")
    bom_id = fields.Many2one("cowork.bom",string="方案设计")