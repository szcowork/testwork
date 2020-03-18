# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class sale_apply(models.Model):
    _name = "sale.apply"
    _description = "销售申请"
    _inherit = ['mail.thread']
    

    name = fields.Char(string="单号",default="New")
    sales = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="销售员")
    date_apply = fields.Date(default=fields.Date.today(), string="申请日期")
    details = fields.Html(string="需求细节")
    partner_id = fields.Many2one("res.partner", "客户", track_visibility="onchange")
    pre_sale_lines = fields.One2many(comodel_name="presale.line", inverse_name="sale_apply_id", string="销售信息")
    pre_purchase_lines = fields.One2many(comodel_name="prepurchase.line", inverse_name="sale_apply_id", string="采购需求")
    abs = fields.Boolean(string="执行备货流程")
    technical_order = fields.Many2one(comodel_name="technical.confirmation", string="技术确认单", track_visibility="onchange")
    contract_state = fields.Selection(selection=[('draft','草稿'),('merchant confirm','商务审批中'),('legal confirm','法务审批中'),('confirm','最终审批中'),('done','确认'),('cancel','取消')], default='draft', string="合同审批状态", track_visibility="onchange")
    scheme_state = fields.Selection(selection=[('draft','草稿'),('confirm','方案审批中'),('done','方案通过'),('cancel','方案不通过')], default='draft', string="方案审批状态", track_visibility="onchange")
    if_standard = fields.Selection(selection=[('nonstandard','非标品'),('standard','标品')], default='nonstandard', string="标品/非标品")

    tc_count = fields.Integer(string='Delivery Orders', compute='_compute_tc_ids')
    sale_order_ids = fields.One2many(comodel_name="sale.order", inverse_name="sale_apply_id", string="生成的销售单据")
    ps_purchase_requisition_ids = fields.One2many(comodel_name="ps.purchase.requisition", inverse_name="sale_apply_id", string="生成的采购单据")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.apply') or '/'
        return super(sale_apply, self).create(vals)

    # 提交技术部门,创建技术单据
    def apply_tc(self):
        tc = self.env['technical.confirmation'].create({
            "sale_apply_id":self.id
        })
    
    # 方案流审批动作
    def sch2draft(self):
        self.scheme_state = 'draft'
    def sch2confirm(self):
        self.scheme_state = 'confirm'
    def sch2done(self):
        self.scheme_state = 'done'
    def sch2cancel(self):
        self.scheme_state = 'cancel'

    # 
    def disconnect_lines(self):
        # self.ensure_one()
        self.technical_order = False
        for line in self.pre_sale_lines:
            line.sale_apply_id = False
        for line in self.pre_purchase_lines:
            line.sale_apply_id = False

    # 合同流审批动作
    def to_draft(self):
        self.contract_state = 'draft'
    def to_merchant_confirm(self):
        self.contract_state = 'merchant confirm'
    def to_legal_confirm(self):
        self.contract_state = 'legal confirm'
    def to_confirm(self):
        self.contract_state = 'confirm'
    def to_done(self):
        self.contract_state = 'done'
    def to_cancel(self):
        self.contract_state = 'cancel'

    # 查看技术方案
    def action_tc_button(self):
        tc_ids = self.env['technical.confirmation'].search([
            ('sale_apply_id', '=', self.id),
        ]).mapped('id')
        if len(tc_ids) > 0 :
            return {
                'name': "技术确认单",
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'technical.confirmation',
                'domain': [('id', 'in', tc_ids)],
            }
        else:
            tc_id = self.env['technical.confirmation'].create({'sale_apply_id':self.id})
            # self.technical_order = tc_id.id
            return {
                'name': "技术确认单",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'technical.confirmation',
                'res_id': tc_id.id,
            }

    def generate_sp_order(self):
        so_lines = []
        for line in self.pre_sale_lines:
            vals = {
                "name":line.product_id.name,
                "product_id": line.product_id.id,
                "product_uom_qty": line.product_qty,
                "product_uom": line.product_uom.id,
                "price_unit": line.product_id.list_price,
                # "order_id": so.id,
                'tax_id': False,
                "customer_lead": 30,
            }
            so_lines.append((0,0,vals))
        # _logger.info(so_lines)
        so = self.env['sale.order'].create({
            "user_id":self.env.user.id,
            "partner_id":self.partner_id.id,
            "order_line":so_lines,
            "sale_apply_id":self.id,
        })
        pre_po_lines = []
        for line in self.pre_purchase_lines:
            vals = {
                "name":line.product_id.name,
                "product_id": line.product_id.id,
                "product_qty": line.product_qty,
                "product_uom_id": line.product_uom.id,
                # "price_unit": line.product_id.standard_price,
                # "requisition_id": po.id,
                "plan_date": fields.Datetime.now(),
            }
            pre_po_lines.append((0,0,vals))
        self.env['ps.purchase.requisition'].create({
            "create_uid":self.env.user.id,
            # "partner_id":self.partner_id.id, 
            "line_ids":pre_po_lines,
            "sale_apply_id":self.id,
        })
        _logger.info('create ps.purchase.requisition')


    # @api.depends('technical_order')
    def _compute_tc_ids(self):
        for order in self:
            tc_ids = self.env['technical.confirmation'].search([
                    ('sale_apply_id', '=', self.id),
                ]).mapped('id')
            order.tc_count = len(tc_ids)