# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_project_estimate(models.Model):
    _name = "cowork.project.estimate"
    _description = "项目评估"
    _inherit = ['mail.thread']

    name = fields.Char(string="项目编号")
    title = fields.Char(string="项目名称")
    project_type = fields.Selection(selection=[('standard', '标准流程'), ('nonstandard', '非标流程')], default="nonstandard", string="项目类型")
    user_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="填单人")
    partner_id = fields.Many2one(comodel_name="res.partner", string="客户名称")
    partner_address = fields.Text(string="客户地址")
    partner_type = fields.Selection(selection=[('new', '新客户'), ('old', '老客户')], default="new", string="客户种类")
    date_of_acceptance = fields.Date(string="接案日期")
    contact_id = fields.Many2one(comodel_name="res.partner", string="联系人")
    budget = fields.Monetary(string="客户预算")
    count = fields.Float(string="预计数量")
    customer_requirement = fields.Html(string="客户需求")
    project_difficulty_id = fields.Many2one(comodel_name="cowork.project.difficulty", string="项目难度")
    cost_budget = fields.Monetary(string="成本预算")
    priority_id = fields.Many2one(comodel_name="cowork.project.priority", string="优先级")
    project_period = fields.Float(string="项目周期")
    count_person = fields.Integer(string="项目人数")
    if_approval = fields.Boolean(string="是否立项")
    comments = fields.Text(string="备注")
    apply_id = fields.Many2one(comodel_name="cowork.project.apply", string="项目申请")
    preliminary_scheme_id = fields.Many2one(comodel_name="cowork.scheme.preliminary", ondelete="cascade", string="项目初步方案")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    state = fields.Selection([
        ('technology','技术部'),
        ('business','商务部'),
        ('project','项目管理部'),
        ('deputy','副总经理'),
        ('general','总经理'),
        ('cancel','无效')
    ],string="状态",default='technology')

    def create_scheme_preliminary(self):
        preliminary = self.env['cowork.scheme.preliminary'].create({
            'apply_id': self.id,
            'title':self.title
        })
        self.preliminary_scheme_id = preliminary.id

    def button_return_estimate_b(self):
        self.state = 'technology'
    def button_estimate_b(self):
        self.state = 'project'
    def button_estimate_t(self):
        self.state = 'business'
    def button_return_estimate_t(self):
        self.state = 'cancel'
    def button_estimate_p(self):
        self.state = 'deputy'
    def button_return_estimate_p(self):
        self.state = 'business'
    def button_estimate_d(self):
        self.state = 'general'
    def button_return_estimate_d(self):
        self.state = 'project'

    def action_to_scheme(self):
        return {
            'name': "项目初步方案",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'cowork.scheme.preliminary',
            # 'domain': [('apply_id', '=', self.id)],
            'domain': [('id','=',self.preliminary_scheme_id.id)]
        }

    def button_back_estimate(self):
        self.state = 'deputy'