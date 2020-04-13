# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import json
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError

class bom_appoval(models.Model):
    _name = "bom.appoval"
    _description = "bom审批"
    _inherit = "einfo.approval"

    @api.model
    def default_get(self, fields):
        res = super(bom_appoval, self).default_get(fields)
        res.update({
        'name': time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        })
        return res

    name = fields.Char(string='单号')
    bom_line_ids = fields.One2many(comodel_name="bom.appoval.line", inverse_name="bom_id",string="bom申请行")
    # picking_type_id = fields.Many2one(comodel_name="stock.picking.type", string="Operation Type")
    # product_id = fields.Many2one(comodel_name="product.product", store=True, string="产品")
    product_qty = fields.Float(required=True, default=1.0, string="数量")
    product_tmpl_id = fields.Many2one(comodel_name="product.template", required=True,string="产品")
    # product_uom_id = fields.Many2one(comodel_name="uom.uom", required=True, default=1, string="单位")
    ready_to_produce = fields.Selection([
        ('all_available', ' 当所有组件都可用时'),
        ('asap', '当第一次操作的组件可用时')],required=True, default='asap', store=True, string="制造准备就绪")
    type = fields.Selection([
        ('normal', '制造此产品'),
        ('phantom', '套件')],required=True, default='normal', store=True, string="BoM 类型")
    technical = fields.Many2one('cowork.technical.analysis',string="技术分析单")
    bom_id = fields.Many2one('mrp.bom',string='物料清单')

    @api.model
    def on_approval(self):
        if self.approval_state == 'pass':
            bom = self.env['mrp.bom'].create({
                'product_tmpl_id':self.product_tmpl_id.id,
                'product_qty':self.product_qty,
                'ready_to_produce':self.ready_to_produce,
                'type':self.type,
                })
            self.write({'bom_id':bom.id})
            for line in self.bom_line_ids:
                bom.bom_line_ids.sudo().create({
                    'bom_id':bom.id,
                    'product_id':line.product_id,
                    'product_qty':line.product_qty
                })
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

class bom_appoval_line(models.Model):
    _name = "bom.appoval.line"
    _description = "BOM 审批行"

    bom_id = fields.Many2one(comodel_name="bom.appoval", required=True, index=True, ondelete="cascade", store=True, string="父级 BoM")
    product_qty = fields.Float(required=True, default=1.0, string="数量")
    # product_tmpl_id = fields.Many2one(comodel_name="product.template",string="组件")
    product_id = fields.Many2one(comodel_name="product.product",string="组件")
