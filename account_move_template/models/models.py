# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class account_move_template(models.Model):
    _name = 'account.move.template'
    _description = u'凭证模板'

    name = fields.Char(u'名称')
    model_id = fields.Many2one("ir.model",u'使用模型')
    journal_id = fields.Many2one("account.journal",u'分录')
    lines = fields.One2many("account.move.template.line","tmpl_id",string="凭证模板明细行")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('Name must be unique!')),
    ]

class account_move_template_line(models.Model):
    _name = 'account.move.template.line'
    _description = u'凭证模板明细行'

    tmpl_id = fields.Many2one("account.move.template",u'模板')
    account_id = fields.Many2one("account.account",u'科目')
    model_id = fields.Many2one("ir.model",u'选定模型')
    att = fields.Selection([('debit',u'借方'),('credit',u'贷方')],string="属性")
    value = fields.Selection([('fixed',u'固定字段'),('code',u'公式代码')],string=u'取值',default='fixed')
    field = fields.Many2one("ir.model.fields",u'固定取值字段')
    field_ids = fields.Many2many('ir.model.fields', 'account_line_field_rel',
                                 'account_line_id', 'field_id', u'字段行')
    model_list = fields.Char('Model List')
    code = fields.Text(u'代码',help=u"使用result=A+B格式",default="result=")

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.field_ids = [(6, 0, [])]
        model_list = []
        if self.model_id:
            model_obj = self.env['ir.model']
            model_list = [self.model_id.id]
            active_model_obj = self.env[self.model_id.model]
            if active_model_obj._inherits:
                keys = active_model_obj._inherits.keys()
                inherits_model_list = model_obj.search([('model', 'in', keys)])
                model_list.extend((inherits_model_list and
                                   inherits_model_list.ids or []))
        self.model_list = model_list
        # _logger.info("444444444444444")
        # _logger.info(model_list)

