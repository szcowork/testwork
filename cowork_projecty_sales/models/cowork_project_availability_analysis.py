# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cowork_project_availability_analysis(models.Model):
    _name = "cowork.project.availability.analysis"
    _description = "项目可行性分析"
    _inherit = ['mail.thread']

    name = fields.Char(string="单号", default="New")
    user_id = fields.Many2one(comodel_name="hr.employee", track_visibility="onchange", string="填表人")
    apply_date = fields.Date(default=fields.Date.today(), string="接案日期")
    ptype = fields.Selection(selection=[('standard', '标准设备'), ('nonstandard', '非标设备')], default="standard", string="项目类型")
    partner_id = fields.Many2one(comodel_name="res.partner", string="客户名称")
    ctype = fields.Selection(selection=[('new', '新客户'), ('old', '老客户')], default="new", string="客户种类")
    address = fields.Text(string="客户地址")
    contact_id = fields.Many2one(comodel_name="res.partner", track_visibility="onchange", string="联系人")
    contact = fields.Char(string="联系方式")
    project_name = fields.Char(track_visibility="onchange", string="项目名称")
    budget_amount = fields.Monetary(track_visibility="onchange", string="采购预算")
    count = fields.Integer(track_visibility="onchange", string="数量")
    description = fields.Html(string="客户需求")
    tech_analysis_id = fields.Many2one(comodel_name="cowork.technical.analysis", string="技术分析")
    project_difiiculty = fields.Many2one(comodel_name="cowork.project.difficulty", string="项目难度")
    cost_amount = fields.Monetary(string="成本预算")
    priority = fields.Many2one(comodel_name="cowork.project.priority", string="优先级")
    period = fields.Float(string="项目周期")
    person_count = fields.Integer(string="项目人数")
    if_start = fields.Boolean(string="是否立项")
    other_description = fields.Html(string="其他技术意见")
    abs = fields.Boolean(string="执行备货流程")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")

    contract_state = fields.Selection(selection=[('draft','草稿'),('merchant confirm','商务审批中'),('legal confirm','法务审批中'),('confirm','最终审批中'),('done','确认'),('cancel','取消')], default='draft', string="合同审批状态", track_visibility="onchange")
    scheme_state = fields.Selection(selection=[('draft','草稿'),('confirm','方案审批中'),('done','方案通过'),('cancel','方案不通过')], default='draft', string="方案审批状态", track_visibility="onchange")
    
    sale_count = fields.Integer(u'销售订单', compute='_compute_sale_count')
    purchase_count = fields.Integer(u'采购订单', compute='_compute_purchase_count')

    @api.one
    def _compute_sale_count(self):
        for record in self:
            order = self.env['sale.order'].sudo().search([('analysis_id','=',self.id)])
            if order:
                record.sale_count = len(order)

    @api.multi
    def action_to_sale(self):
        pass
    
    def action_create_sale_order_new(self):
        return {
            'name': u'销售订单',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': self.env.ref('sale.view_order_form').id,
            # 'target': 'new',
            'context': {
                    'default_technical': self.id,
                    'default_partner_id':self.partner_id.id,
            }
        }
    
    @api.one
    def _compute_purchase_count(self):
        for record in self:
            order = self.env['purchase.order'].sudo().search([('analysis_id','=',self.id)])
            if order:
                record.purchase_count = len(order)

    @api.multi
    def action_to_purchase(self):
        pass

    def action_create_purchase_order_new(self):
        return {
            'name': u'采购订单',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
            # 'target': 'new',
            'context': {
                    'default_technical': self.id,
                    'default_partner_id':self.partner_id.id,
            }
        }

    @api.model
    def create(self, vals): 
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('cowork.project.availability.analysis') or '/' #创建时自动生成单号
        return super(cowork_project_availability_analysis, self).create(vals)

    # 提交技术部门,创建技术单据
    def apply_tc(self):
        tc = self.env['cowork.technical.analysis'].create({
            'project_availability_analysis_id':self.id,
            'if_nonstandard_scheme': True if self.ptype == 'nonstandard' else False,
            'if_nonstandard_quote': True if self.ptype == 'nonstandard' else False,
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
    def tc_ids(self):
        tc_ids = self.env['cowork.technical.analysis'].search([
            ('project_availability_analysis_id', '=', self.id),
        ]).mapped('id')

        return {
            'name': "技术性分析",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'cowork.technical.analysis',
            'domain': [('id', 'in', tc_ids)],
        }