# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_quote_order(models.Model):
    _name = "cowork.quote.order"
    _description = "项目报价单"
    
    name = fields.Char(default="New", string="单号")
    project_id = fields.Many2one(comodel_name="cowork.project.apply", string="项目编号")
    title = fields.Char(string="项目名称")
    partner_id = fields.Many2one(comodel_name="res.partner", string="客户名称")
    contact_id = fields.Many2one(comodel_name="res.partner", string="联系人")
    material_cost_details_lines = fields.One2many(comodel_name="cowork.cost.material.detail.line.quote", inverse_name="quote_id", string="组件")
    labor_cost_lines = fields.One2many(comodel_name="cowork.cost.labor.quote", inverse_name="quote_id", string="人力成本")
    state = fields.Selection([
        ('business','商务部'),
        ('technology','技术部'),
        ('project','项目管理部'),
        ('deputy','副总经理'),
        ('general','总经理'),
        ('cancel','无效')
    ],string="状态",default='business')

    amount = fields.Monetary(string="合计", store=True, compute='_amount_all')
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")

    @api.model
    def create(self, vals): 
         #创建时自动生成单号
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('cowork.quote.order') or '/'
        return super(cowork_quote_order, self).create(vals)

    def button_return_estimate_b(self):
        self.state = 'cancel'
    def button_estimate_b(self):
        self.state = 'technology'
    def button_estimate_t(self):
        self.state = 'project'
    def button_return_estimate_t(self):
        self.state = 'business'
    def button_estimate_p(self):
        self.state = 'deputy'
    def button_return_estimate_p(self):
        self.state = 'technology'
    def button_estimate_d(self):
        self.state = 'general'
    def button_return_estimate_d(self):
        self.state = 'project'
    def button_return_estimate_g(self):
        self.state = 'deputy'
    def action_to_draft(self):
        self.state = 'business'

    def action_to_bom(self):
        return {
            'name': "物料方案",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cowork.bom',
            'view_id': self.env.ref('cowork_project_management_flow.view_form_cowork_bom').id,
            'context': {
                    'default_quote_id': self.id,
            }
        }
    
    def button_material_scheme_order(self):
        tc_ids = self.env['cowork.bom'].search([
            ('name', '=', self.id),
        ]).mapped('id')
        return {
            'name': "物料方案",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'cowork.bom',
            'domain': [('id','=',tc_ids)]
        }

    @api.depends('labor_cost_lines.total_quote','material_cost_details_lines.sale_cost')
    def _amount_all(self):
        for order in self:
            amount = 0.0
            if order.labor_cost_lines:
                for line in order.labor_cost_lines:
                    amount += line.total_quote
            if order.material_cost_details_lines:
                for line in order.material_cost_details_lines:
                    amount += line.sale_cost

            order.update({
                'amount': amount,
            })