# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_technical_analysis(models.Model):
    _name = "cowork.technical.analysis"
    _description = "技术分析"
    _inherit = ['mail.thread']

    name = fields.Char(string="单号", default="New")
    user_id = fields.Many2one(string="填单人")
    project_availability_analysis_id = fields.Many2one(comodel_name="cowork.project.availability.analysis", string="项目可行性分析单")
    efficiency_beat = fields.Float(string="效率节拍")
    robot_model_id = fields.Many2one(comodel_name="product.product", string="机器人型号")
    plc_controller = fields.Many2one(comodel_name="product.product", string="PLC控制器")
    module = fields.Many2one(comodel_name="product.product", string="模组")
    sensor = fields.Many2one(comodel_name="product.product", string="传感器")
    cylinder = fields.Many2one(comodel_name="product.product", string="气缸")
    fixture = fields.Many2one(comodel_name="product.product", string="治具")
    motor = fields.Many2one(comodel_name="product.product", string="电机配置")
    ccd_vision = fields.Many2one(comodel_name="product.product", string="CCD视觉")
    industry = fields.Many2one(comodel_name="res.partner.industry", string="样品行业")
    sample_name = fields.Char(string="样品名称")
    pneumatic_components = fields.Many2one(comodel_name="product.product", string="气动元件")
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