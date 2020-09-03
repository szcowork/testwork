from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


# class EinfoCodeRule(models.Model):
#     _name = "einfo.code.rule"

#     name = fields.Char('编号类型')
#     number_next = fields.Integer(string='下一个号码')
#     ir_sequence_id = fields.Many2one('ir.sequence')


# class IrSequence(models.Model):
#     _inherit = "ir.sequence"
#     is_einfo_code_ids = fields.Boolean('是否管理内部编号')

#     einfo_code_ids = fields.One2many(
#         'einfo.code.rule', 'ir_sequence_id', string=u'code',)

class RuleContext(models.Model):
    _name = "rule.context"
    _description = "规则"

    name = fields.Char('名称')
    value = fields.Char('值')
    einfo_code_rule_line_id = fields.Many2one('einfo.code.rule.line')


class EinfoCodeRuleLine(models.Model):
    _name = "einfo.code.rule.line"
    _description = "规则行"

    name = fields.Char('名称')
    einfo_code_rule_id = fields.Many2one('einfo.code.rule')
    ttype = fields.Selection([('select', '选择类型'),('sequence', '流水号'),('char', '手动输入')],string='类型',default="select")
    ir_sequence_id = fields.Many2one('ir.sequence',string='序列号')
    rule_context_ids = fields.One2many(
        'rule.context', 'einfo_code_rule_line_id', string=u'详细描述',)


class GenerateCodeLine(models.Model):
    _name = "generate.code.line"
    _description = "编号行"

    name = fields.Char('编号')
    description = fields.Text('说明')
    einfo_code_rule_id = fields.Many2one('einfo.code.rule')


class EinfoCodeRule(models.Model):
    _name = "einfo.code.rule"
    _description = '编号类型'
    

    name = fields.Char('编号类型')
    tem_generate_code = fields.Char('生成编号', default="???")
    einfo_code_rule_line_ids = fields.One2many(
        'einfo.code.rule.line', 'einfo_code_rule_id', string=u'规则行',)
    generate_code_line_ids = fields.One2many(
        'generate.code.line', 'einfo_code_rule_id', string=u'生成编号行',)


    # 返回值
    # [
    #      {
    #          ttype: 'select',
    #          data: [['A', '行政管理部'], ['B', '商务部'], ['F', '财务部'], ['T', '技术部']]
    #      },
    #      {
    #          ttype: 'select',
    #          data: [['A', '单机'], ['B', '工具'], ['C', '气压组件'], ['E', '电料'], ['H', '五金类'], ['P', '耗材'], ['R', '机器人']]
    #      },
    #  ]
    @api.model
    def get_rule_data(self,id):
        rule = self.browse([id])[0]
        result = []
        for rule_line in rule.einfo_code_rule_line_ids:
            tem_rule = {}
            tem_rule['name'] = rule_line.name
            if rule_line.ttype == 'select':
                tem_rule['ttype'] = 'select'
                tem_rule['data'] = []
                for rule_context in rule_line.rule_context_ids:
                    tem_rule['data'].append([rule_context.value,rule_context.name])
                result.append(tem_rule)
            if rule_line.ttype == 'sequence':
                tem_rule['ttype'] = 'sequence'
                tem_rule['data'] = rule_line.id
                result.append(tem_rule)
            if rule_line.ttype == 'char':
                tem_rule['ttype'] = 'char'
                result.append(tem_rule)
        return result

    @api.model
    def get_sequence(self,id):
        rule_line = self.env['einfo.code.rule.line'].search([('id','=',id)])
        result = ''
        if(rule_line):
            # result = rule_line[0].ir_sequence_id.next_by_id()
            ir_sequence_id = rule_line[0].ir_sequence_id
            if not ir_sequence_id.use_date_range:
                number_next_actual = ir_sequence_id.number_next_actual
                result = ir_sequence_id.get_next_char(number_next_actual)
            else:
                dt = fields.Date.today()
                seq_date = self.env['ir.sequence.date_range'].search([('sequence_id', '=',ir_sequence_id.id), ('date_from', '<=', dt), ('date_to', '>=', dt)], limit=1)
                if not seq_date:
                    seq_date = ir_sequence_id._create_date_range_seq(dt)
                number_next_actual = seq_date.number_next_actual
                result = ir_sequence_id.get_next_char(number_next_actual)
        return result


    @api.model
    def generate_code(self,id,code,description):
        rule = self.browse([id])[0]
        _logger.info(rule)
        rule.write({'generate_code_line_ids':[(0,0,{
            'name':code,
            'description':description,
            'einfo_code_rule_id':id
        })]})
        return 'ok'

    @api.model
    def generate_code_client_action(self,id,code,model_name,model_id,field_name,sequence_rule_lines):
        rule = self.browse([id])[0]
        rule.write({'generate_code_line_ids':[(0,0,{
            'name':code,
            'einfo_code_rule_id':id
        })]})
        sequence_rule_lines = self.env['einfo.code.rule.line'].browse(sequence_rule_lines)
        for sequence_rule_line in sequence_rule_lines:
            # _logger.info(sequence_rule_line)
            sequence_rule_line.ir_sequence_id.next_by_id()
        model = self.env[model_name].browse([model_id])[0]
        model.sudo().write({field_name:code})
        return 'ok'

class Wizard(models.TransientModel):
    _name = 'einfo.code.rule.wizard'


    @api.model
    def default_get(self, fields):
        # _logger.info('default_get----------')
        rec = super(Wizard, self).default_get(fields)
        rec.update({
        'einfo_code_rule_id': self._context.get('einfo_code_rule_id'),
        'name': self._context.get('name'),
        'sequence_rule_lines':self._context.get('sequence_rule_lines'),
        })
        return rec


    einfo_code_rule_id = fields.Many2one('einfo.code.rule',)
    sequence_rule_lines = fields.Many2many('einfo.code.rule.line')
    name = fields.Char('编号')
    description = fields.Text('说明')


    def comfirm(self):
        self.einfo_code_rule_id.write({'generate_code_line_ids':[(0,0,{
            'name':self.name,
            'description':self.description,
            'einfo_code_rule_id':self.einfo_code_rule_id.id
        })]})
        for sequence_rule_line in self.sequence_rule_lines:
            _logger.info(sequence_rule_line)
            sequence_rule_line.ir_sequence_id.next_by_id()
        # self.einfo_code_rule_id.ir_sequence_id.next_by_id()
        return {'type': 'ir.actions.act_window_close'}