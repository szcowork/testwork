# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_attachment_line(models.Model):
    _name = "cowork.attachment.line"
    _description = "附件行"
    

    apply_id = fields.Many2one(comodel_name="cowork.project.apply", ondelete="cascade", string="立项申请")
    url = fields.Char(required=True, string="链接地址")
