# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _inherit = 'sale.order'

    analysis_id = fields.Many2one("cowork.project.availability.analysis",string=u'项目可行性分析')

class ps_purchase_requisition(models.Model):
    _inherit = 'ps.purchase.requisition'

    analysis_id = fields.Many2one("cowork.project.availability.analysis",string=u'项目可行性分析')