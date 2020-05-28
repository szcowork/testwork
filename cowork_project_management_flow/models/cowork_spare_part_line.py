# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_spare_part_line(models.Model):
    _name = "cowork.spare.part.line"
    _description = "零部件成本行"
    

    material_detail_line = fields.Many2one(comodel_name="cowork.cost.material.detail.line", ondelete="cascade", string="组件物料成本行")
    material_detail_line_quote = fields.Many2one(comodel_name="cowork.cost.material.detail.line.quote", ondelete="cascade", string="组件物料成本行")
    categ_id = fields.Many2one(comodel_name="product.category", string="名称")
    product_tmpl_id = fields.Many2one(comodel_name="product.template", string="规格")
    brand_id = fields.Many2one(comodel_name="product.brand", string="品牌")
    count = fields.Float(string="数量")
    unit_price = fields.Monetary(string="单价")
    total_price = fields.Monetary(string="合计")
    premium_coefficient = fields.Float(string='溢价系数')
    comments = fields.Text(string="备注")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    
    uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    premium_no = fields.Float("溢价系数")

    @api.onchange('unit_price','count')
    def _onchange_total_price(self):
        self.total_price = self.unit_price * self.count

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.uom_id = self.product_tmpl_id.uom_po_id or self.product_tmpl_id.uom_id
         
        else:
            self.uom_id = False


class cowork_spare_part_line_quote(models.Model):
    _name = "cowork.spare.part.line.quote"
    _description = "零部件成本行"
    
    material_detail_line = fields.Many2one(comodel_name="cowork.cost.material.detail.line", ondelete="cascade", string="组件物料成本行")
    material_detail_line_quote = fields.Many2one(comodel_name="cowork.cost.material.detail.line.quote", ondelete="cascade", string="组件物料成本行")
    categ_id = fields.Many2one(comodel_name="product.category", string="名称")
    product_tmpl_id = fields.Many2one(comodel_name="product.template", string="规格")
    brand_id = fields.Many2one(comodel_name="product.brand", string="品牌")
    count = fields.Float(string="数量")
    unit_price = fields.Monetary(string="单价")
    total_price = fields.Monetary(string="合计")
    premium_coefficient = fields.Float(string='溢价系数')
    comments = fields.Text(string="备注")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    
    uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    premium_no = fields.Float("溢价系数")

    @api.onchange('unit_price','count')
    def _onchange_total_price(self):
        self.total_price = self.unit_price * self.count

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.uom_id = self.product_tmpl_id.uom_po_id or self.product_tmpl_id.uom_id
         
        else:
            self.uom_id = False