# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

class reimbursement_appoval(models.Model):
    _name = "reimbursement.appoval"
    _description = "报销申请"
    _inherit = "einfo.approval"

    @api.model
    def default_get(self, fields):
        res = super(reimbursement_appoval, self).default_get(fields)
        res.update({
        'name': time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        })
        return res

    name = fields.Char(required=True, string="单号")
    # eply = fields.Many2one(comodel_name="hr.employee", required=True, string="员工")
    department = fields.Many2one(comodel_name="hr.department", required=True, string="部门")
    # posi = fields.Many2one('hr.job',required=True, related="eply.job_id", string="岗位")
    business_period = fields.Date(required=True, string="业务期间")
    #reimbursement_account = fields.One2many(comodel_name="reimbursement.account",  required=True, string="报销科目")
    account_name = fields.Char(required=True, string="收款方账户名称")
    bank_name = fields.Char(required=True, string="银行名称")
    bank_code = fields.Char(required=True, string="银行账号")
    total = fields.Float(required=True, string="合计金额")
    invoice_document = fields.Binary(required=True, string="发票文件上传")
