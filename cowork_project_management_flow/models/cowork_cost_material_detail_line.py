# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_cost_material_detail_line(models.Model):
    _name = "cowork.cost.material.detail.line"
    _description = "组件物料成本行"
    

    cost_material_line = fields.Many2one(comodel_name="cowork.cost.material", ondelete="cascade", string="物料成本行")
    preliminary_scheme_id = fields.Many2one(comodel_name="cowork.scheme.preliminary", ondelete="cascade", string="项目初步方案")
    name = fields.Char(string="组件名称")
    count = fields.Float(string="单台数量")
    unit_cost = fields.Monetary(string="单台成本")
    class_id = fields.Many2one(comodel_name="cowork.material.class", string="类型")
    spare_parts_lines = fields.One2many(comodel_name="cowork.spare.part.line", inverse_name="material_detail_line", string="零部件")
    total_cost = fields.Monetary(string="成本")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    cowork_bom_id = fields.Many2one("cowork.bom",string="物料方案")
    state = fields.Selection([
        ('project','项目管理部'),
        ('business','商务部'),
    ],string="状态",related='preliminary_scheme_id.state')

    def edit_spare_parts(self):
        return {
            'name': "-".join([self.class_id.name, self.name]) if self.class_id else self.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cowork.cost.material.detail.line',
            'type': 'ir.actions.act_window',
            # 'target': 'current',
            'target': 'new',
            'res_id': self.id,
            'view_id':self.env.ref('cowork_project_management_flow.view_form_cowork_cost_material_detail_line').id,
            'context':{
                'form_view_initial_mode':'edit'
            }
        }
    
    def compute_total_price(self):
        tmp = 0.0
        for line in self.spare_parts_lines:
            tmp += line.total_price
        self.unit_cost = tmp
        self.total_cost = self.unit_cost * self.count

    def trans_quote(self, quote):
        q = self.env['cowork.cost.material.detail.line.quote'].create({
            'quote_id': quote.id,
            'name':self.name,
            'count':self.count,
            'unit_cost':self.unit_cost,
            'class_id':self.class_id.id,
            'total_cost':self.total_cost,
            'currency_id':self.currency_id.id,
        })
        # for line in self.spare_parts_lines:
        #     line.material_detail_line_quote = q.id
        if self.spare_parts_lines:
            for spare in self.spare_parts_lines:
                q.spare_parts_lines.create({
                    'categ_id': spare.categ_id.id if spare.categ_id else False,
                    'product_tmpl_id':spare.product_tmpl_id.id if spare.product_tmpl_id else False,
                    'brand_id':spare.brand_id.id if spare.brand_id else False,
                    'count':spare.count,
                    'unit_price':spare.unit_price,
                    'total_price':spare.total_price,
                    'comments':spare.comments,
                    'uom_id':spare.uom_id.id if spare.uom_id else False,
                    'material_detail_line_quote':q.id
                })