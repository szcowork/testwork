# -*- coding: utf-8 -*-

from odoo import models, fields, api


class prepurchase_line(models.Model):
    _name = "prepurchase.line"
    _description = "采购信息"
    

    sale_apply_id = fields.Many2one(comodel_name="sale.apply", string="销售申请")
    tc_order_id = fields.Many2one(comodel_name="technical.confirmation", string="技术确认")
    product_id = fields.Many2one(comodel_name="product.product", string="产品")
    product_qty = fields.Float(string="数量" , default=1.0)
    product_uom = fields.Many2one(comodel_name="uom.uom", string="单位")
    comment = fields.Char(string="备注")


    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id