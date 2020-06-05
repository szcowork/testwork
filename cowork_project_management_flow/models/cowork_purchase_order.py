# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class cowork_purchase_order(models.Model):
    _name = "cowork.purchase.order"
    _description = "柯沃申购"
    _inherit = ['mail.thread']

    name = fields.Char(string="设备名称/组件名称")
    class_id = fields.Many2one("cowork.material.class",string="分类")
    code = fields.Char(string="设备编号")
    user_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="编制")
    date = fields.Date(default=fields.Date.today(), string="日期")
    qty = fields.Float(string="数量")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    line_id = fields.One2many("cowork.purchase.order.line","order_id",string="申购明细")
    amount = fields.Monetary(string="总计", store=True, compute='_amount_all')
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    project_id = fields.Many2one("cowork.project.apply",string="项目编号")
    state = fields.Selection([('draft','草稿'),('confirm','确认'),('purchase','已生成询价单'),('cancel','取消')],string="状态",default='draft')

    @api.depends('line_id.amount')
    def _amount_all(self):
        for order in self:
            amount = 0.0
            for line in order.line_id:
                amount += line.amount
            order.update({
                'amount': amount,
            })

    def button_order(self):
        self.state = 'confirm'

    def button_to_purchase(self):
        self.state = 'purchase'
        if self.line_id:
            record = {}
            for line in self.line_id:
                if not record.__contains__(str(line.partner_id.id)):
                    purchase = self.env['purchase.order'].create({
                        'partner_id':line.partner_id.id,
                        'date_order': fields.Datetime.now(),
                        'user_id': self.env.user.id,
                        'project_id': line.order_id.project_id.id
                    })
                    record[str(line.partner_id.id)] = purchase
                else:
                    purchase = record[str(line.partner_id.id)]

                tax = []
                if line.tax_ids:
                    for taxes in line.tax_ids:
                        tax.append(taxes.id)

                purchase.order_line.create({
                    'order_id':purchase.id,
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_qty': line.product_qty,
                    'product_uom': line.uom_id.id,
                    'taxes_id': [(6, 0, tax)],
                    'price_unit': line.list_price,
                    'date_planned': fields.Datetime.now()
                })

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one("cowork.project.apply",string="项目编号")

    @api.multi
    def button_confirm(self):
        super(purchase_order, self).button_confirm()
        picking = self.env['stock.picking'].search([('origin','=',self.name)])
        if picking:
            picking[0].project_id = self.project_id.id

class cowork_purchase(models.Model):
    _name = 'cowork.purchase'
    _description = "拟询价单"

    name = fields.Char(string="名称")
    line_id = fields.One2many("cowork.purchase.order.line","purchase_id",string="申购明细")
    pline_id = fields.One2many("cowork.purchase.line","purchase_id",string="申购明细")
    apply_time = fields.Datetime("申请时间")
    user_id = fields.Many2one(comodel_name="res.users", string="采购员")

    def return_purchase(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/cowork_quote/%s' % (self.id),
            'target': 'current',  
        }
    
    def generate_plines(self):
        pids = []
        line_id = self.line_id

        for line in line_id:
            pids.append(line.product_id.id)
        pids = list(set(pids))
        length = len(pids)

        if self.pline_id:
            self.pline_id.unlink()
        for index in range(length):
            count = 0
            lines = []
            tax = []
            for line in line_id:
                if line.product_id.id == pids[index]:
                    if line.tax_ids:
                        for t in line.tax_ids:
                            tax.append(t.id)
                    count += line.product_qty
                    lines.append(line.id)
            rec = self.env['cowork.purchase.order.line'].search([('id','=',lines[0])])
            vals = {
                'partner_id':rec.partner_id.id,
                'categ_id':rec.categ_id.id,
                'product_id':rec.product_id.id,
                'product_qty': count,
                'uom_id':rec.uom_id.id,
                'material':rec.material,
                'type_id':rec.type_id.id,
                'brand_id':rec.brand_id.id,
                'list_price':0,
                'tax_ids':[(6, 0, tax)],
                'delivery':0,
                'comment': rec.comment,
                'purchase_id':rec.purchase_id.id,
                'line_ids':[(6, 0, lines)]
            }
            self.env['cowork.purchase.line'].create(vals)
                

    def update_purchase(self):
        for line in self.pline_id:
            tax=[]
            for t in line.tax_ids:
                tax.append(t.id)
            for l in line.line_ids:
                l.update({
                    'partner_id':line.partner_id,
                    'list_price':line.list_price,
                    'tax_ids':[(6, 0, tax)],
                    'delivery':line.delivery,
                    'comment':line.comment
                })


class cowork_purchase_line(models.Model):
    _name = "cowork.purchase.line"
    _description = "柯沃采购明细行"
    
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
    purchase_id = fields.Many2one("cowork.purchase",string="拟询价")
    line_ids = fields.Many2many(comodel_name="cowork.purchase.order.line", string="关联申购明细行")
    
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
            'currency_id': self.currency_id,
            'product_qty': self.product_qty,
            'product': self.product_id,
        }