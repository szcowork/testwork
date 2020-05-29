# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class cowork_bom(models.Model):
    _name = 'cowork.bom'
    _description = '物料方案'

    material_details_ids = fields.One2many('cowork.cost.material.detail.line','cowork_bom_id',string="组件信息")
    # name = fields.Many2one("cowork.scheme.preliminary",string="项目初步方案")
    name = fields.Many2one("cowork.quote.order",string="项目报价单")
    project_id = fields.Many2one(comodel_name="cowork.project.apply", string="项目编号")
    material_cost_details_lines = fields.One2many(comodel_name="cowork.bom.material", inverse_name="bom_id", string="组件物料成本明细")

    def get_material_info(self):
        if self.name:
            if self.name.material_cost_details_lines:
                self.material_cost_details_lines = False
                for detail in self.name.material_cost_details_lines:
                    bom_material = self.env['cowork.bom.material'].create({
                        'bom_id':self.id,
                        'name':detail.name,
                        'count':detail.count,
                        'class_id':detail.class_id.id,
                    })
                    if detail.spare_parts_lines:
                        for spare in detail.spare_parts_lines:
                            bom_material.spare_parts_lines.create({
                                'categ_id':spare.categ_id.id,
                                'product_tmpl_id':spare.product_tmpl_id.id,
                                'brand_id':spare.brand_id.id,
                                'count':spare.count,
                                'comments':spare.comments,
                                'uom_id':spare.uom_id.id,
                                'material_id':bom_material.id
                            })

    @api.one
    def action_to_requisition(self):
        # pass
        if self.material_cost_details_lines:
            employee = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
            employee_id = False
            department_id = False
            if employee:
                employee_id = employee[0].id
                if employee[0].department_id:
                    department_id = employee[0].department_id.id

            pre_po_lines = []
            for bom in self.material_cost_details_lines:
                if bom.spare_parts_lines:
                    for part in bom.spare_parts_lines:
                        vals = {
                            "name":part.product_tmpl_id.product_variant_id.name,
                            "product_id": part.product_tmpl_id.product_variant_id.id,
                            "product_qty": part.count,
                            "product_uom_id": part.uom_id.id,
                            "plan_date": fields.Datetime.now(),
                        }
                        pre_po_lines.append((0,0,vals))
            self.env['ps.purchase.requisition'].create({
                "create_uid":self.env.user.id,
                "line_ids":pre_po_lines,
                "sale_cowork_id":self.name.id,
                'employee_id':employee_id,
                'requisition_date':fields.Date.today(),
                'department_id':department_id,
                'project_sale_id':self.project_id.id
            })
            _logger.info("ps.purchase.requisition")

class cowork_bom_material(models.Model):
    _name = 'cowork.bom.material'

    bom_id = fields.Many2one("cowork.bom",string="物料方案")

    # preliminary_scheme_id = fields.Many2one(comodel_name="cowork.scheme.preliminary",string="项目初步方案",related="bom_id.name")
    preliminary_scheme_id = fields.Many2one(comodel_name="cowork.quote.order",string="项目报价单",related="bom_id.name")
    name = fields.Char(string="组件名称")
    count = fields.Float(string="单台数量")
    class_id = fields.Many2one(comodel_name="cowork.material.class", string="分类")
    spare_parts_lines = fields.One2many(comodel_name="cowork.bom.material.part", inverse_name="material_id", string="零部件")

    def edit_spare_parts(self):
        return {
            'name': "-".join([self.class_id.name, self.name]) if self.class_id else self.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cowork.bom.material',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
            'view_id':self.env.ref('cowork_project_management_flow.view_form_cowork_bom_material').id,
            'context':{
                'form_view_initial_mode':'edit'
            }
        }

class cowork_bom_material_part(models.Model):
    _name = "cowork.bom.material.part"

    categ_id = fields.Many2one(comodel_name="product.category", string="名称")
    product_tmpl_id = fields.Many2one(comodel_name="product.template", string="规格")
    brand_id = fields.Many2one(comodel_name="product.brand", string="品牌")
    count = fields.Float(string="数量")
    comments = fields.Text(string="备注")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    material_id = fields.Many2one("cowork.bom.material",string="物料")

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.uom_id = self.product_tmpl_id.uom_po_id or self.product_tmpl_id.uom_id


class ps_purchase_requisition(models.Model):
    _inherit = "ps.purchase.requisition"

    sale_cowork_id = fields.Many2one("cowork.quote.order",string="项目报价单")
    project_sale_id = fields.Many2one(comodel_name="cowork.project.apply", string="项目编号")