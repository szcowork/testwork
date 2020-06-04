# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_purchase_order_line(models.Model):
    _name = "cowork.purchase.order.line"
    _description = "柯沃采购明细行"
    
    order_id = fields.Many2one(comodel_name="cowork.purchase.order", string="设备名称/组件")
    categ_id = fields.Many2one(comodel_name="product.category", string="图号/名称")
    product_id = fields.Many2one(comodel_name="product.product", string="名称/型号")
    product_qty = fields.Float(string="数量")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    material = fields.Char(string="材料")
    type_id = fields.Many2one(comodel_name="purchase.type", string="类型")
    brand_id = fields.Many2one(comodel_name="product.brand", string="品牌")
    partner_id = fields.Many2one(comodel_name="res.partner", string="供应商")
    list_price = fields.Monetary(string="含税单价")
    tax_ids = fields.Many2many("account.tax", string="税率")
    amount = fields.Monetary(compute='_compute_amount',string="含税金额",store=True)
    delivery = fields.Integer(string="货期(天)")
    comment = fields.Text(string="备注")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    subtotal = fields.Monetary(compute='_compute_amount',string="不含税金额",store=True)
    project_id = fields.Many2one('cowork.project.apply', related='order_id.project_id', string='项目编号', readonly=True, store=True)
    state = fields.Selection([('draft','草稿'),('confirm','确认'),('purchase','已生成询价单'),('cancel','取消')],string="状态",related='order_id.state')
    purchase_id = fields.Many2one("cowork.purchase",string="拟询价")

    @api.depends('product_qty', 'list_price', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.tax_ids.compute_all(
                vals['list_price'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'])
            line.update({
                # 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'amount': taxes['total_included'],
                'subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'list_price': self.list_price,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
        }

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        self.price_unit = self.product_qty = 0.0
        self.uom_id = self.product_id.uom_po_id or self.product_id.uom_id
        self.tax_ids = False
        result['domain'] = {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        return result

    @api.multi
    def action_be_purchase(self):
        purchase = self.env['cowork.purchase'].create({
            'name':str(fields.Datetime.now())
        })
        for order in self:
            order.purchase_id = purchase.id

class purchase_type(models.Model):
    _name = 'purchase.type'

    name = fields.Char(string="类型名称")