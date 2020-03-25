# -*- coding: utf-8 -*-

from odoo import models, fields, api
import random
import time
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError

class sequence_rule(models.Model):
    _name = 'sequence.rule'
    _description = u'组合规则'

    name =  fields.Char(u'组合序号名称')
    model_id = fields.Many2one("ir.model",string=u'模型说明')
    model = fields.Char(string=u'模型',related='model_id.model')
    rule_lines = fields.One2many("sequence.rule.line","rule_id",string="规则行")
    company_id = fields.Many2one('res.company',string='公司',default=lambda self: self._get_company())

    @api.model
    def _get_company(self):
        return self._context.get('company_id', self.env.user.company_id.id)


class sequence_rule_line(models.Model):
    _name = 'sequence.rule.line'
    _description = u'组合规则行'

    rule_id = fields.Many2one("sequence.rule")
    rule_type = fields.Selection([('field',u'字段值'),('sequence',u'序列号')],string="规则类型")  #,('diy',u'自定义')
    field_id = fields.Many2one('ir.model.fields',string="字段")
    sequence_id = fields.Many2one('ir.sequence',string='序列号')
    model_id = fields.Many2one("ir.model",string=u'模型说明')
    select_lines = fields.One2many('select.line','sequence_line_id',string=u'对照表')
    company_id = fields.Many2one('res.company',string='公司')

    @api.onchange('field_id')
    def onchange_field_id(self):
        if self.select_lines:
            for sele in self.select_lines:
                sele.write({'sequence_line_id': False})

    def get_field_info(self):
        if self.field_id.ttype == 'selection':
            selection = self.env[self.model_id.model]._fields[self.field_id.name].selection
            if isinstance(selection,list):
                for elem in selection:
                    self.select_lines.sudo().create({
                        'key':elem[0],
                        'sequence_line_id':self.id
                    })
        if self.field_id.ttype == 'many2one':
            record = self.env[self.field_id.relation].sudo().search([])
            if record:
                for rec in record:
                    self.select_lines.sudo().create({
                        'key':rec.name,
                        'sequence_line_id':self.id
                    })


class select_line(models.Model):
    _name = 'select.line'

    sequence_line_id = fields.Many2one("sequence.rule.line")
    key = fields.Char(u'键')
    value = fields.Char(u'值')
