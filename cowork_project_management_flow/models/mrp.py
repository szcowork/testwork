# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class mrp_bom(models.Model):
    _inherit = 'mrp.bom'

    def action_to_requisition(self):
        _logger.info("requisition")
        if self.bom_line_ids:
            requisition = self.env['purchase.requisition'].create({
                'user_id':self.env.user.id,
            })
            for bom in self.bom_line_ids:
                requisition.line_ids.create({
                    'product_id':bom.product_id.id,
                    'product_qty':bom.product_qty,
                    'product_uom_id':bom.product_uom_id.id,
                    'requisition_id':requisition.id
                })