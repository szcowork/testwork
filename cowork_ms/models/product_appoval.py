# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import json
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError
class product_appoval(models.Model):
    _name = "product.appoval"
    _description = "产品审批"
    _inherit = "einfo.approval"

    @api.model
    def default_get(self, fields):
        res = super(product_appoval, self).default_get(fields)
        res.update({
        'name': time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) 
        })
        return res

    name = fields.Char(required=True, string="单号")

    reason = fields.Text(required=True, string="说明")
    rule_id = fields.Many2one('einfo.code.rule',string='编号类型')
    product_code = fields.Char('生成编号', default="???")
    product_id = fields.Many2one('product.template',string='产品')
    product_code_template_widget = fields.Text('编号规则', compute='_get_product_code_template_widget_JSON', default="???")

    department = fields.Many2one("department.info",string="使用部门")
    categ_id = fields.Many2one("product.category",string="产品种类")
    factory_id = fields.Many2one("factory.info",string="厂牌")
    rule = fields.Many2one('sequence.rule',string='编号规则')

    # other_element = fields.Many2many("product.appoval",string=u'组件申请')

    # @api.onchange('rule_id')
    # def rule_onchange(self):
    #     _logger.info('rule_onchange')
    #     self.tem_code = '???'
    @api.one
    def button_get_code(self):
        if self.rule:
            rule = self.rule
            if rule.rule_lines:
                no = ''
                sequence_ids = []
                for ru in rule.rule_lines:
                    if ru.rule_type == 'field':
                        # if vals_list.get(ru.field_id.name) == False:
                        if self[ru.field_id.name].id == False:
                            raise UserError(('请填写%s！')%(ru.field_id.field_description))
                        if ru.field_id.ttype not in ['selection','many2one']:
                            no += str(self[ru.field_id.name])
                        if ru.field_id.ttype == 'selection':
                            if ru.select_lines:
                                value = False
                                for select in ru.select_lines:
                                    if self[ru.field_id.name] == select.key:
                                        value = select.value
                                if value == False:
                                    raise UserError(u'请配置键值表！')
                                else:
                                    no += value
                            else:
                                raise UserError(u'请配置键值表！')
                        if ru.field_id.ttype == 'many2one':
                            if ru.select_lines:
                                value = False
                                record = self.env[ru.field_id.relation].search([('id','=',self[ru.field_id.name].id)])
                                for select in ru.select_lines:
                                    if record.name == select.key:
                                        value = select.value
                                if value == False:
                                    raise UserError(u'请配置键值表！')
                                else:
                                    no += value
                            else:
                                raise UserError(u'请配置键值表！')
                    if ru.rule_type == 'sequence':#序列号
                        number_next_actual = ru.sequence_id.number_next_actual
                        no += ru.sequence_id.get_next_char(number_next_actual)
                        sequence_ids.append(ru.sequence_id)
                
                # has_partner = self.env['product.template'].sudo().search([('ref','=',no)])
                # if has_partner:
                #     raise UserError(u'产品编号已存在！')
                # has_applyfor = self.env['product.appoval'].sudo().search([('ref','=',no)])
                # if has_applyfor:
                #     raise UserError(u'产品编号已存在！')
                self.product_code = no
                if len(sequence_ids) > 0:
                    for seq in sequence_ids:
                        seq.next_by_id()
        else:
            raise ValidationError(u'请选择编号规则!')

    @api.model
    def on_approval(self):
        if self.approval_state == 'pass':
            product = self.env['product.template'].create({'name':self.product_code,'default_code':self.product_code,
            'department':self.department.id,
            'categ_id':self.categ_id.id,
            'type':'product',
            'factory_id':self.factory_id.id})
            self.write({'product_id':product.id})
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        if self.rule_id:
            return {
                    'type': 'ir.actions.client',
                    'name': '编码生成',
                    'tag': 'action_einfo_code',
                    'target': 'new',
                    'context': {'rule_id': self.rule_id.id,'model_name':'product.appoval','model_id':self.id,'field_name':'product_code'},
                    }

    @api.one
    def _get_product_code_template_widget_JSON(self):
        self.product_code_template_widget = json.dumps(False)
        if self.rule_id:
            info = self.rule_id.get_rule_data(self.rule_id.id)
            self.product_code_template_widget = json.dumps(info)

class department_info(models.Model):
    _name = 'department.info'

    name = fields.Char(u'部门名称')
    
class factory_info(models.Model):
    _name = 'factory.info'

    name = fields.Char(u'厂牌名称')

class product_product(models.Model):
    _inherit = "product.product"

    department = fields.Many2one("department.info",string="使用部门")
    factory_id = fields.Many2one("factory.info",string="厂牌")

class product_template(models.Model):
    _inherit = "product.template"

    department = fields.Many2one("department.info",string="使用部门")
    factory_id = fields.Many2one("factory.info",string="厂牌")