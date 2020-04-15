# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _inherit = 'sale.order'

    analysis_id = fields.Many2one("cowork.project.availability.analysis",string=u'项目可行性分析')

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    analysis_id = fields.Many2one("cowork.project.availability.analysis",string=u'项目可行性分析')