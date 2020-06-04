# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class cowork_purchase_order(models.Model):
    _name = "cowork.purchase.order"
    _description = "柯沃采购"
    _inherit = ['mail.thread']

    name = fields.Char(string="设备名称/组件名称")
    class_id = fields.Many2one("cowork.material.class",string="分类")
    code = fields.Char(string="设备编号")
    user_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="编制")
    date = fields.Date(default=fields.Date.today(), string="日期")
    qty = fields.Float(string="数量")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    line_id = fields.One2many("cowork.purchase.order.line","order_id",string="采购明细")
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

class cowork_purchase(models.Model):
    _name = 'cowork.purchase'
    _description = "拟询价单"

    name = fields.Char(string="名称")
    line_id = fields.One2many("cowork.purchase.order.line","purchase_id",string="申购明细")

    def return_purchase(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/cowork_quote/%s' % (self.id),
            'target': 'current',  
        }
            
