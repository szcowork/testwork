# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_cost_material_detail_line(models.Model):
    _name = "cowork.cost.material.detail.line.quote"
    _description = "组件物料成本行"
    
    cost_material_line = fields.Many2one(comodel_name="cowork.cost.material", ondelete="cascade", string="物料成本行")
    name = fields.Char(string="组件名称")
    count = fields.Float(string="单台数量")
    unit_cost = fields.Monetary(string="单台成本")
    total_cost = fields.Monetary(string="成本")
    unit_quote = fields.Monetary(string='单台报价')
    total_quote = fields.Monetary(string='总报价')
    class_id = fields.Many2one(comodel_name="cowork.material.class", string="类型")
    # spare_parts_lines = fields.One2many(comodel_name="cowork.spare.part.line", inverse_name="material_detail_line_quote", string="零部件")
    spare_parts_lines = fields.One2many(comodel_name="cowork.spare.part.line.quote", inverse_name="material_detail_line_quote", string="零部件")
    quote_id = fields.Many2one(comodel_name="cowork.quote.order", ondelete="cascade", string="项目报价单")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    sale_cost = fields.Monetary("价格")
    state = fields.Selection([
        ('business','商务部'),
        ('technology','技术部'),
        ('project','项目管理部'),
        ('deputy','副总经理'),
        ('general','总经理'),
        ('cancel','无效')
    ],string="状态",related='quote_id.state')

    def edit_spare_parts(self):
        return {
            'name': "-".join([self.class_id.name, self.name]) if self.class_id else self.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cowork.cost.material.detail.line.quote',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
            'view_id':self.env.ref('cowork_project_management_flow.view_form_cowork_cost_material_detail_line_quote').id,
            'context':{
                'form_view_initial_mode':'edit'
            }
        }
    
    def compute_total_price(self):
        tmp = 0.0
        for line in self.spare_parts_lines:
            tmp += line.total_price
        self.total_cost = tmp
