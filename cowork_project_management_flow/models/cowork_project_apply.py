# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class cowork_project_apply(models.Model):
    _name = "cowork.project.apply"
    _description = "立项申请"
    _inherit = ['mail.thread']

    name = fields.Char(string="项目编号", default="???")  #New
    rule_id = fields.Many2one('einfo.code.rule',string='编号类型')
    # product_code_template_widget = fields.Text('编号规则', compute='_get_product_code_template_widget_JSON', default="???")
    # @api.one
    # def _get_product_code_template_widget_JSON(self):
    #     self.product_code_template_widget = json.dumps(False)
    #     if self.rule_id:
    #         info = self.rule_id.get_rule_data(self.rule_id.id)
    #         self.product_code_template_widget = json.dumps(info)

    @api.onchange('rule_id')
    def rule_onchange(self):
        self.name = '???'

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        if self.rule_id:
            _logger.info("??????????????")
            return {
                    'type': 'ir.actions.client',
                    'name': '编码生成',
                    'tag': 'action_einfo_code',
                    'target': 'new',
                    'context': {'rule_id': self.rule_id.id,'model_name':'cowork.project.apply','model_id':self.id,'field_name':'name'},
                    }

    date_apply = fields.Date(default=fields.Date.today(), string="申请日期")
    user_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="业务申请人")
    location_apply = fields.Char(string="申请地点")
    title = fields.Char(string="项目名称")
    partner_id = fields.Many2one(comodel_name="res.partner", string="客户名称")
    partner_type = fields.Selection(selection=[('new', '新客户'), ('old', '老客户')], default="new", string="客户类型")
    partner_address = fields.Text(string="客户地址")
    budget = fields.Monetary(string="客户项目预算")
    count = fields.Float(string="项目预计数量")
    date_deliver = fields.Date(string="客户预计交期")
    customer_comment = fields.Text(string="客户信息备注")
    charger_lines = fields.One2many(comodel_name="cowork.project.charger", inverse_name="apply_id", track_visibility="onchange", string="项目负责人")
    comments = fields.Text(string="其他事项")
    customer_requirement = fields.Html(string="客户需求")
    estimate_id = fields.Many2one(comodel_name="cowork.project.estimate", string="项目评估")
    requirement_attament_lines = fields.One2many(comodel_name="cowork.attachment.line", inverse_name="apply_id", string="需求附件")
    # requirement_attament = fields.Char("需求附件地址")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    state = fields.Selection([
        ('business','商务部'),
        ('project','项目管理部'),
    ],string="状态",default='business')

    # @api.model
    # def create(self, vals): 
    #      #创建时自动生成单号
    #     if vals.get('name', 'New') == 'New':
    #         vals['name'] = self.env['ir.sequence'].next_by_code('cowork.project.apply') or '/'
    #     return super(cowork_project_apply, self).create(vals)

    def create_estimate(self):
        e = self.env['cowork.project.estimate'].create({
            'apply_id':self.id,
            'name': self.name,
            'title': self.title,
            'partner_id':self.partner_id.id,
            'partner_address':self.partner_address,
            'budget':self.budget,
            'count':self.count,
            'customer_requirement':self.customer_requirement,
            'partner_type':self.partner_type,
            'date_of_acceptance':self.date_apply,
            'user_id': self.user_id.id
        })
        self.estimate_id = e.id
    
    @api.onchange('partner_id')
    def _onchange_address(self):
        partner = self.partner_id
        if partner:
            self.partner_address = "".join([
                partner.country_id.name if partner.country_id else "",
                partner.state_id.name if partner.state_id else "", 
                partner.city if partner.city else "",
                partner.street if partner.street else "",
                partner.street2 if partner.street2 else ""
            ])
        else:
            self.partner_address = ""

    def action_to_project(self):
        self.state = 'project'

    def action_to_estimate(self):
        # self.env['cowork.project.estimate'].search([('apply_id','=',self.id)])
        return {
            'name': "项目评估",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'cowork.project.estimate',
            'domain': [('id', '=', self.estimate_id.id)],
        }

    def button_return_apply(self):
        self.state = 'business'

    def action_to_purchase(self):
        tc_ids = self.env['purchase.order'].search([
            ('project_id', '=', self.id),
        ]).mapped('id')
        return {
            'name': "采购单",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'purchase.order',
            'domain': [('id','in',tc_ids)]
        }