# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_scheme_preliminary(models.Model):
    _name = "cowork.scheme.preliminary"
    _description = "项目初步方案"
    _inherit = ['mail.thread']

    name = fields.Char(string="单号", default="New")
    title = fields.Char(string="项目名称")
    user_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="填单人")
    date_fill = fields.Date(default=fields.Date.today(), string="填单时间")
    apply_id = fields.Many2one(comodel_name="cowork.project.estimate", string="项目编号")
    labor_cost_lines = fields.One2many(comodel_name="cowork.cost.labor", inverse_name="preliminary_scheme_id", string="人力成本")
    material_cost_lines = fields.One2many(comodel_name="cowork.cost.material", inverse_name="preliminary_scheme_id", string="物料成本")
    total_labor_cost = fields.Monetary(string="合计人力成本")
    total_material_cost = fields.Monetary(string="合计物料成本")
    total_untaxed_cost = fields.Monetary(string="合计未税成本")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    material_cost_details_lines = fields.One2many(comodel_name="cowork.cost.material.detail.line", inverse_name="preliminary_scheme_id", string="组件物料成本明细")
    quote_id = fields.Many2one(comodel_name="cowork.quote.order", ondelete="cascade", string="项目报价单")
    state = fields.Selection([
        ('technology','技术部'),
        ('business','商务部'),
    ],string="状态",default='technology', track_visibility='onchange')

    def action_to_business(self):
        self.state = 'business'
        self.summary_all()

    @api.model
    def create(self, vals): 
         #创建时自动生成单号
        if vals.get('name', 'New') == 'New':
            vals['name'] =self.apply_id.name +"/"+ self.env['ir.sequence'].next_by_code('cowork.scheme.preliminary') or '/'
        return super(cowork_scheme_preliminary, self).create(vals)

    def import_categs(self):
        categs = self.env['cowork.material.category'].search([])
        for categ in categs:
            self.env['cowork.cost.material'].create({
                "material_categ_id":categ.id,
                "preliminary_scheme_id":self.id,
            })

    def summary_all(self):
        tmp = 0.0
        for line in self.labor_cost_lines:
            tmp += line.total_price
        self.total_labor_cost = tmp

        for line in self.material_cost_details_lines:
            line.compute_total_price()

        tmp = 0.0
        for line in self.material_cost_lines:
            line.compute_total_price()
            tmp += line.total_price
        self.total_material_cost = tmp
        self.total_untaxed_cost = self.total_material_cost + self.total_labor_cost

    def create_quote(self):
        estimate = self.apply_id
        quote = self.env['cowork.quote.order'].create({
            'project_id':estimate.apply_id.id,
            'title':estimate.title,
            'partner_id':estimate.partner_id.id,
            'contact_id':estimate.contact_id.id,
        })
        self.quote_id = quote.id
        for line in self.labor_cost_lines:
            line.trans_quote(quote)
        for line in self.material_cost_details_lines:
            line.trans_quote(quote)

    def button_to_requisition(self):
        return {
            'name': "项目报价单",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'cowork.quote.order',
            'domain': [('id','=',self.quote_id.id)]
        }

    def button_return_scheme(self):
        self.state = 'technology'