# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class contract_approval(models.Model):
    _name = "contract.approval"
    _description = "合同"
    _inherit = ['mail.thread']

    name = fields.Char(string="合同名称")
    date = fields.Date(string="申请日期",default=fields.Date.context_today)
    purchase_id = fields.Many2one("purchase.order",string="采购订单")
    # sale_id = fields.Many2one('sale.order',string="销售订单")
    sale_id = fields.Many2one(comodel_name="sale.order",string="销售订单")
    approval_date = fields.Date(string="审批日期",track_visibility="onchange")
    contract_ids = fields.One2many("cowork.contact","approval_id",string="文件")
    comments = fields.Text(string="备注")
    state = fields.Selection([('draft','草稿'),('director','商务总监审批'),('general','综合管理部审批'),('managerment','总经理审批'),('pass','通过')],default='draft',string="状态",track_visibility="onchange")
    need_mark = fields.Boolean(string="是否用印")

    def action_to_director(self):
        self.state = 'director'

    def action_to_general(self):
        self.state = 'general'

    def back_to_draft(self):
        self.state = 'draft'

    def action_to_managerment(self):
        self.state = 'managerment'
        
    def back_to_diector(self):
        self.state = 'diector'

    def action_to_pass(self):
        self.state = 'pass'
        self.approval_date = fields.Date.today()

    def back_to_general(self):
        self.state = 'general'

class cowork_contact(models.Model):
    _name = "cowork.contact"

    contract = fields.Binary(string="文件")
    name = fields.Char(string="备注")
    approval_id = fields.Many2one("contract.approval",string="合同")


    
