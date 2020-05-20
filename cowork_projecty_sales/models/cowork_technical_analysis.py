# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_technical_analysis(models.Model):
    _name = "cowork.technical.analysis"
    _description = "技术分析"
    _inherit = ['mail.thread']

    name = fields.Char(string="单号", default="New")
    user_id = fields.Many2one(comodel_name="res.users", string="填单人")
    project_availability_analysis_id = fields.Many2one(comodel_name="cowork.project.availability.analysis", string="项目可行性分析单")
    efficiency_beat = fields.Float(string="效率节拍")
    industry = fields.Many2one(comodel_name="res.partner.industry", string="样品行业")
    sample_name = fields.Char(string="样品名称")
    if_proof = fields.Boolean(string="已打样")
    if_proof_before_sell = fields.Boolean(string="出厂前打样")
    if_proof_on_site = fields.Boolean(string="交货现场打样")
    if_nonstandard_scheme = fields.Boolean(string="非标方案")
    if_nonstandard_quote = fields.Boolean(string="非标报价")
    if_tech_contract = fields.Boolean(string="有技术协议")
    internal_code = fields.Char(string="设备内部型号")
    internal_name = fields.Char(string="设备内部名称")
    cost_amount = fields.Monetary(string="成本预算")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    priority = fields.Many2one(comodel_name="cowork.project.priority", string="优先级")
    person_count = fields.Integer(string="项目人数")
    period = fields.Float(string="项目周期")
    other_description = fields.Html(string="其他技术意见")
    if_start = fields.Boolean(string="是否立项")
    project_difiiculty = fields.Many2one(comodel_name="cowork.project.difficulty", string="项目难度")
    state = fields.Selection(selection=[('draft','草稿'),('confirm','审批中'),('done','确认'),('cancel','取消')], default='draft', string="状态", track_visibility="onchange")

    
    # approval_pro_count = fields.Integer(u'申请产品数', compute='_compute_approval_pro')
    # approval_bom_count = fields.Integer(u'申请BOM表数', compute='_compute_approval_bom')
    technical_id = fields.One2many("cowork.project.technical","technical_id",string=u'技术参数')

    # @api.one
    # def one_action_to_approval(self):
    #     product = self.env['product.appoval'].sudo().search([('technical','=',self.id),('approval_state','=','draft')]) 
    #     if product:
    #         for pro in product:
    #             pro.approval_state = 'approvaling'
                
        # bom = self.env['bom.appoval'].sudo().search([('technical','=',self.id),('approval_state','=','draft')])
        # if bom:
        #     for bo in bom:
        #         bo.approval_state = 'approvaling'

    # @api.one
    # def _compute_approval_bom(self):
    #     for record in self:
    #         approval = self.env['bom.appoval'].sudo().search([('technical','=',self.id)])
    #         if approval:
    #             record.approval_bom_count = len(approval)
    
    # @api.multi
    # def action_approval_bom(self):
    #     action = {
    #         'name': u'申请BOM表',
    #         'view_mode': 'tree,form',
    #         'res_model': 'bom.appoval',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #         'domain': [('technical', '=', self.id)]
    #     }
    #     return action

    # def action_to_approval_bom(self):
    #     return {
    #         'name': u'申请BOM表',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'bom.appoval',
    #         'view_id': self.env.ref('cowork_ms.view_form_bom_appoval').id,
    #         'target': 'new',
    #         'context': {
    #                 'default_technical': self.id,
    #         }
    #     }

    # @api.one
    # def _compute_approval_pro(self):
    #     for record in self:
    #         approval = self.env['product.appoval'].sudo().search([('technical','=',self.id)])
    #         if approval:
    #             record.approval_pro_count = len(approval)

    # def action_to_approval(self):
    #     return {
    #         'name': u'申请产品',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'product.appoval',
    #         'view_id': self.env.ref('cowork_ms.view_form_einfo_approval').id,
    #         'target': 'new',
    #         'context': {
    #                 'default_technical': self.id,
    #         }
    #     }

    # @api.multi
    # def action_approval_pro(self):
    #     action = {
    #         'name': u'申请产品',
    #         'view_mode': 'tree,form',
    #         'res_model': 'product.appoval',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #         'domain': [('technical', '=', self.id)]
    #     }
    #     return action

    @api.model
    def create(self, vals): 
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('cowork.technical.analysis') or '/' #创建时自动生成单号
        return super(cowork_technical_analysis, self).create(vals)

    
    # 状态流审批动作
    def to_draft(self):
        self.state = 'draft'
    def to_confirm(self):
        self.state = 'confirm'
        # self.tech_user = self.env.user
    def to_done(self):
        self.state = 'done'
        self.sync_consq()
    def to_cancel(self):
        self.state = 'cancel'

    def sync_consq(self):
        if self.project_availability_analysis_id:
            vals = {
                'tech_analysis_id':self.id,
                'project_difiiculty': self.project_difiiculty.id,
                'cost_amount':self.cost_amount,
                'priority':self.priority.id,
                'period':self.period,
                'person_count':self.person_count,
                'if_start':self.if_start,
                'other_description':self.other_description
            }
            self.env["cowork.project.availability.analysis"].search([('id','=',self.project_availability_analysis_id.id)]).write(vals)