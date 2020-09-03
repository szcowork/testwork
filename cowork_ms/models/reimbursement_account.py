# -*- coding: utf-8 -*-

from odoo import models, fields, api


class reimbursement_account(models.Model):
    _name = "reimbursement.account"
    _description = "报销科目"


   # name = fields.Char(required=True, string="单号")
    name = fields.Char(required=True, string="科目名称")
    subject_up = fields.Many2one(comodel_name="reimbursement.account", string="上级科目")
