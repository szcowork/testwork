# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)
class technical_confirmation(models.Model):
    _name = "technical.confirmation"
    _description = "技术确认"
    _inherit = ['mail.thread']

    @api.model
    def default_get(self, fields):
        rec = super(technical_confirmation, self).default_get(fields)
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model == 'sale.apply' and active_id:
            sale_apply = self.env['sale.apply'].search([('id', '=', active_id)])
            rec.update({'sale_apply_id': sale_apply.id})
        return rec
    

    name = fields.Char(string="单号",default="New")
    tech_user = fields.Many2one(comodel_name="res.users", string="技术人员")
    pre_sale_line = fields.One2many(comodel_name="presale.line", inverse_name="tc_order_id", string="销售信息", track_visibility="onchange")
    pre_purchase_line = fields.One2many(comodel_name="prepurchase.line", inverse_name="tc_order_id", string="采购信息", track_visibility="onchange")
    sale_apply_id = fields.Many2one(comodel_name="sale.apply", string="销售申请单")
    date_handle = fields.Date(default=fields.Date.today(), string="处理日期")
    state = fields.Selection(selection=[('draft','草稿'),('confirm','审批中'),('done','确认'),('cancel','取消')], default='draft', string="状态", track_visibility="onchange")

    new_sale_product_ids = fields.Many2many(comodel_name="product.product",relation="new_sale_product_ref", string="新产品")
    new_purchase_product_ids = fields.Many2many(comodel_name="product.product",relation="new_purchase_product_ref", string="新产品")


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('technical.confirmation') or '/'
        return super(technical_confirmation, self).create(vals)

    # 状态流审批动作
    def to_draft(self):
        self.state = 'draft'
    def to_confirm(self):
        self.state = 'confirm'
        self.tech_user = self.env.user

    @api.multi
    def to_done(self):
        self.ensure_one()
        self.state = 'done'
        sale_apply_id = self.sale_apply_id
        _logger.info('to_done')
        sale_apply_id.disconnect_lines()
        sale_apply_id.technical_order = self.id
        sale_apply_id.sch2confirm()

        #如果pre_sale_line pre_purchase_line没有包含就加入
        # tem_product_ids = []
        # for tem in self.pre_sale_line:
        #     tem_product_ids.append(tem.product_id.id)
        # for item in self.new_sale_product_ids:
        #     if item.id not in tem_product_ids:
        #         self.write({'pre_sale_line':[(0,0,{'product_id':item.id,'product_qty':1.0,'tc_order_id':self.id,'product_uom':item.uom_id.id})]})
        # tem_product_ids = []
        # for tem in self.pre_purchase_line:
        #     tem_product_ids.append(tem.product_id.id)
        # for item in self.new_purchase_product_ids:
        #     if item.id not in tem_product_ids:
        #         self.write({'pre_purchase_line':[(0,0,{'product_id':item.id,'product_qty':1.0,'tc_order_id':self.id,'product_uom':item.uom_id.id})]})

        for line in self.pre_sale_line:
            line.sale_apply_id = sale_apply_id
        for line in self.pre_purchase_line:
            line.sale_apply_id = sale_apply_id
    def to_cancel(self):
        self.state = 'cancel'

    # @api.onchange('new_sale_product_ids')
    # def on_new_sale_product_ids_change(self):
    #     _logger.info(self.new_sale_product_ids.mapped('id'))
        # items = self.pre_sale_line.mapped('id')
        # for sale_product in self.new_sale_product_ids:
        #     if sale_product.id not in items:
        #         _logger.info(sale_product.id)
        #         self.write({'pre_sale_line':[(0, 0, {'product_id':2,'product_qty':1.0,'tc_order_id':13})]})

