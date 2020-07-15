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
    approval_date = fields.Date(string="审批日期")
    contract_ids = fields.One2many("cowork.contact","approval_id",string="文件")
    comments = fields.Text(string="备注")
    state = fields.Selection([('draft','草稿'),('director','商务总监审批'),('general','综合管理部审批'),('managerment','总经理审批'),('pass','通过')],default='draft',string="状态")
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

    def back_to_general(self):
        self.state = 'general'

class cowork_contract(models.Model):
    _name = "cowork.contact"

    contract = fields.Binary(string="文件")
    name = fields.Char(string="备注")
    approval_id = fields.Many2one("contract.approval")


access_contract_approval_merchant_assistant,contract_approval:商务助理,model_contract_approval,access_group_merchant_assistant_in_cowork_project_management_flow,1,1,1,1
access_contract_approval_merchant_director,contract_approval:商务总监,model_contract_approval,access_group_merchant_director_in_cowork_project_management_flow,1,1,1,1
access_contract_approval_general_manager_director,contract_approval:综合事业部总经理,model_contract_approval,general_managerment_director,1,1,1,1
access_contract_approval_general_manager,contract_approval:总经理,model_contract_approval,access_group_general_manager_in_cowork_project_management_flow,1,1,1,1

    
