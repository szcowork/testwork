# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
    
class stock_picking(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one("cowork.project.apply", string="项目编号")
    employee_id = fields.Many2one("hr.employee",string="申请人")

class stock_move(models.Model):
    _inherit = 'stock.move'

    project_id = fields.Many2one("cowork.project.apply", string="项目编号",related="picking_id.project_id")
