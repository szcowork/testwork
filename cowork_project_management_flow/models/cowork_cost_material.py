# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_cost_material(models.Model):
    _name = "cowork.cost.material"
    _description = "物料成本行"
    

    preliminary_scheme_id = fields.Many2one(comodel_name="cowork.scheme.preliminary", ondelete="cascade", string="项目初步方案")
    material_categ_id = fields.Many2one(comodel_name="cowork.material.category", string="项目")
    total_price = fields.Monetary(string="总价")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    material_cost_details_lines = fields.One2many(comodel_name="cowork.cost.material.detail.line", inverse_name="cost_material_line", string="组件物料成本明细")
    state = fields.Selection([
        ('project','项目管理部'),
        ('business','商务部'),
    ],string="状态",related='preliminary_scheme_id.state')

    def edit_details(self):
        return {
            'name': self.material_categ_id.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cowork.cost.material',
            'type': 'ir.actions.act_window',
            # 'target': 'current',
            'target': 'new',
            'res_id': self.id,
            'view_id':self.env.ref('cowork_project_management_flow.view_form_cowork_cost_material').id,
            'context':{
                'form_view_initial_mode':'edit'
            }
        }

    def compute_total_price(self):
        tmp = 0.0
        for line in self.material_cost_details_lines:
            line.compute_total_price()
            tmp += line.total_cost
        self.total_price = tmp
