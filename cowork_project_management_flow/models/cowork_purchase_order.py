# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError

class cowork_purchase_order(models.Model):
    _name = "cowork.purchase.order"
    _description = "柯沃申购"
    _inherit = ['mail.thread', 'mail.activity.mixin','portal.mixin']

    name = fields.Char(string="设备名称/组件名称")
    class_id = fields.Many2one("cowork.material.class",string="类型")
    code = fields.Char(string="设备编号")
    user_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="编制")
    date = fields.Date(default=fields.Date.today(), string="日期")
    # qty = fields.Float(string="数量")
    # uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    line_id = fields.One2many("cowork.purchase.order.line","order_id",string="申购明细",copy=True)
    # amount = fields.Monetary(string="单件总计", store=True, compute='_amount_all')
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    project_id = fields.Many2one("cowork.project.apply",string="项目编号")
    state = fields.Selection([('draft','草稿'),('confirm','确认'),('purchase','已生成采购单'),('cancel','取消')],string="状态",default='draft')
    amount_total = fields.Monetary(string="合计", store=True, compute='_amount_all')
    count = fields.Float(string="项目数量",default=1.0)
    this_count = fields.Float(string="本次采购数量",default=1.0)

    @api.one
    @api.depends('line_id.amount')
    def _amount_all(self):
        for order in self:
            amount = 0.0
            for line in order.line_id:
                amount += line.amount
            
            order.update({
                # 'amount': amount,
                'amount_total': amount
            })

    def button_order(self):
        self.state = 'confirm'

    @api.one
    def button_cancel(self):
        self.state = 'cancel'

    def button_draft(self):
        self.state = 'draft'

    def button_to_purchase(self):
        self.state = 'purchase'
        if self.line_id:
            record = {}
            for line in self.line_id:
                line.bom_line_id.has_purchase = True
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
                date_planned = fields.Date.today() + timedelta(days=line.delivery)
                purchase.order_line.create({
                    'order_id':purchase.id,
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_qty': line.product_qty,
                    'product_uom': line.uom_id.id,
                    'taxes_id': [(6, 0, tax)],
                    'price_unit': line.list_price,
                    'date_planned': date_planned#fields.Datetime.now()
                })

                purchase.button_confirm()

    def action_to_change_info(self):
        order_line = self.env['cowork.material.change'].search([('purchase_id','=',self.id)]).mapped('id')
        return {
            'name': "柯沃申购物料更改",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'cowork.material.change',
            # 'views': [
            #     (self.env.ref('cowork_project_management_flow.view_tree_cowork_purchase_order_line').id, 'tree'),
            # ],
            'domain': [('id', 'in', order_line)],
        }

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one("cowork.project.apply",string="项目编号")
    invoice_type = fields.Selection([('no','未收到票'),('part','已收部分票据'),('all','已收全部票据')],default='no', track_visibility='onchange',string="发票状态",copy=False)
    payment_state = fields.Selection([('no','未申请'),('draft','申请'),('leader','组长审批'),('manager','采购总监审批'),('general','总经理审批'),('done','完成')],string="付款状态审批流",default='no',copy=False)
    payment_type = fields.Selection([('no','未付款'),('part','已付部分款'),('all','已支付全款')],default='no', track_visibility='onchange',string="付款状态",compute='_compute_payment_type')

    pay_type = fields.Selection([('prepay','预付'),('final','全款/尾款')],string="付款方式",default='final')
    payment_amount = fields.Float(string="支付金额",default=100.0)
    prepay_method = fields.Selection([('percentage','预付百分比'),('fixed','预付固定金额')],string="预付方式")

    purchase_approval_state = fields.Selection([('draft','申请'),('leader','组长审批'),('manager','总监审批'),('general','总经理审批'),('pass','通过')],default='draft',string="采购审批",track_visibility='onchange',copy=False)
    purchase_contact = fields.Many2one("contract.approval",string="合同")

    def purchase_user_refuse(self):
        self.purchase_approval_state = 'draft'

    def payment_user_refuse(self):
        self.payment_state = 'draft'
        
    def test_test(self):
        self.payment_state = 'general'

    def plan_to_payment(self):
        self.payment_state = 'draft'

    def approval_to_payment(self):
        if self.payment_amount > self.amount_total:
            raise UserError('支付金额不能大于采购总额！')
        if self.purchase_contact:
            self.payment_state = 'leader'
        else:
            raise UserError('请关联合同!')

    def approval_to_payment_to_draft(self):
        self.payment_state = 'no'

    def lead_pass_payment(self):
        self.payment_state = 'manager'

    def lead_refuse_payment(self):
        self.payment_state = 'draft'

    def manager_pass_payment(self):
        self.payment_state = 'general'

    def mamager_refuse_payment(self):
        self.payment_state = 'manager'

    def general_pass_payment(self):
        if self.pay_type == 'prepay':
            if self.prepay_method == 'percentage':
                amount = self.amount_total * self.payment_amount / 100.0
            if self.prepay_method == 'fixed':
                amount = self.payment_amount
            journal = self.env['account.journal'].search([('type','=','bank')])
            self.env['account.payment'].sudo().create({
                'payment_type': 'outbound',
                'partner_id': self.partner_id.id,
                'amount': amount,
                'purchase_id': self.id,
                'payment_method_id':1,
                'journal_id': journal[0].id,
                'partner_type': 'supplier'
            })
            self.payment_state = 'no'
            self.payment_type = 'part'
            self.pay_type = 'final'

        elif self.pay_type == 'final':
            self.payment_state = 'done'
            action = self.env.ref('account.action_vendor_bill_template')
            result = action.read()[0]
            create_bill = self.env.context.get('create_bill', False)
            result['context'] = {
                'type': 'in_invoice',
                'default_purchase_id': self.id,
                'default_currency_id': self.currency_id.id,
                'default_company_id': self.company_id.id,
                'company_id': self.company_id.id
            }
            if len(self.invoice_ids) > 1 and not create_bill:
                result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
            else:
                res = self.env.ref('account.invoice_supplier_form', False)
                result['views'] = [(res and res.id or False, 'form')]
                if not create_bill:
                    result['res_id'] = self.invoice_ids.id or False
            result['context']['default_origin'] = self.name
            result['context']['default_reference'] = self.partner_ref
            result['state'] = 'draft'
            return result

    @api.one
    def _compute_payment_type(self):
        invoice = self.env['account.invoice'].search([('type','=','in_invoice'),('origin','=',self.name),('state','=','paid')])
        if invoice:
            self.payment_type = 'all'
        else:
            payment = self.env['account.payment'].search([('purchase_id','=',self.id),('state','=','posted')])
            if payment:
                self.payment_type = 'part'

    def button_to_approval(self):
        self.purchase_approval_state = 'leader'

    def button_to_leader(self):
        self.purchase_approval_state = 'manager'
    
    def back_to_draft(self):
        self.purchase_approval_state = 'draft'

    def button_to_manager(self):
        self.purchase_approval_state = 'general'

    def back_to_lead(self):
        self.purchase_approval_state = 'leader'

    def button_to_general(self):
        self.purchase_approval_state = 'pass'
        self.button_confirm()

    def back_to_manager(self):
        self.purchase_approval_state = 'general'

    @api.multi
    def button_confirm(self):
        super(purchase_order, self).button_confirm()
        picking = self.env['stock.picking'].search([('origin','=',self.name)])
        if picking:
            picking[0].project_id = self.project_id.id

    @api.multi
    def action_view_payment(self):
        action = self.env.ref('account.action_account_payments_payable')
        result = action.read()[0]
        result['context'] = {}
        payment = self.env['account.payment'].search([('purchase_id','=',self.id)])
        _logger.info(payment)
        res = self.env.ref('account.view_account_payment_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = payment.id
        return result

class cowork_purchase(models.Model):
    _name = 'cowork.purchase'
    _description = "拟询价单"
    _inherit = ['mail.thread', 'mail.activity.mixin','portal.mixin']

    name = fields.Char(string="名称")
    line_id = fields.One2many("cowork.purchase.order.line","purchase_id",string="申购明细",copy=True)
    pline_id = fields.One2many("cowork.purchase.line","purchase_id",string="申购明细",copy=True)
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
            product_qty = 0
            lines = []
            tax = []
            for line in line_id:
                if line.product_id.id == pids[index]:
                    if line.tax_ids:
                        for t in line.tax_ids:
                            tax.append(t.id)
                    product_qty += line.product_qty
                    lines.append(line.id)
            rec = self.env['cowork.purchase.order.line'].search([('id','=',lines[0])])
            vals = {
                'partner_id':rec.partner_id.id,
                'categ_id':rec.categ_id.id,
                'product_id':rec.product_id.id,
                'product_qty': product_qty,
                'uom_id':rec.uom_id.id,
                'material':rec.material,
                # 'type_id':rec.type_id.id,
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

class account_payment(models.Model):
    _inherit = 'account.payment'

    purchase_id = fields.Many2one("purchase.order",string="采购订单")
    payment_state = fields.Selection([('draft','草稿'),('approval','总监审批'),('pass','通过'),('cancel','取消')],default='draft',copy=False,string="付款审批")

    def button_to_approval(self):
        self.payment_state = 'approval'

    def back_to_draft(self):
        self.payment_state = 'draft'

    def button_to_pass(self):
        self.payment_state = 'pass'
        self.post()

    def account_user_refuse(self):
        self.payment_state = 'cancel'
        self.state = 'cancelled'

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    approval_state = fields.Selection([('draft','草稿'),('approval','总监审批'),('pass','通过'),('cancel','取消')],string="审批状态",default='draft')

    def account_user_refuse(self):
        self.approval_state = 'cancel'
        self.state = 'cancel'
        if self.origin:
            purchase = self.env['purchase.order'].search([('name','=',self.origin)])
            if purchase:
                purchase.payment_state = 'no'
                for line in purchase.order_line:
                    line.invoice_lines = False

    def button_to_approval(self):
        self.approval_state = 'approval'

    def button_to_pass(self):
        self.approval_state = 'pass'
        self.action_invoice_open()

    def button_to_draft(self):
        self.approval_state = 'draft'
    