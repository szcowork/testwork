# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError

class cowork_bom(models.Model):
    _name = 'cowork.bom'
    _description = '物料方案'
    _inherit = ['mail.thread']

    material_details_ids = fields.One2many('cowork.cost.material.detail.line','cowork_bom_id',string="组件信息")
    name = fields.Many2one("cowork.quote.order",string="项目报价单")
    project_id = fields.Many2one(comodel_name="cowork.project.apply", string="项目编号")
    material_cost_details_lines = fields.One2many(comodel_name="cowork.bom.material", inverse_name="bom_id", string="组件物料成本明细")
    mechaine_pic = fields.Char(string="机械3D图")
    electric_pic = fields.Char(string="电气3D图")
    state = fields.Selection([('draft','草稿'),('approval','审批中'),('confirm','确认')],default='draft',string='状态')

    spare_parts_lines = fields.One2many(comodel_name="cowork.bom.material.part", inverse_name="bom_id", string="零部件", track_visibility='onchange')
    # spare_parts_lines_c = fields.One2many(comodel_name="cowork.bom.material.part", inverse_name="bom_id_c", string="更新零部件", track_visibility='onchange')
    count = fields.Float(string="项目数量")
    # max_delay = fields.Integer(string="最长货期")

    cowork_message_ids = fields.One2many(comodel_name="cowork.message",inverse_name="bom_id",string="更改信息")

    def get_material_info(self):
        if self.name:
            if self.name.material_cost_details_lines:
                self.material_cost_details_lines = False
                for detail in self.name.material_cost_details_lines:
                    if detail.spare_parts_lines:
                        for spare in detail.spare_parts_lines:
                            # bom_material.spare_parts_lines.create({
                            self.spare_parts_lines.create({
                                'categ_id':spare.categ_id.id,
                                'product_tmpl_id':spare.product_tmpl_id.id,
                                'brand_id':spare.brand_id.id,
                                'count':spare.count * detail.count,
                                'comments':spare.comments,
                                'uom_id':spare.uom_id.id,
                                'bom_id':self.id,
                                'class_id': detail.class_id.id,
                                'class_categ_id': detail.class_id.categ_id.id
                            })

    @api.one
    def action_to_requisition(self):
        order = self.env['cowork.purchase.order'].search([('project_id','=',self.project_id.id),('state','!=','purchase')])
        order_t = self.env['cowork.purchase.order'].search([('project_id','=',self.project_id.id),('state','!=','cancel')])
        if order:#只有一张草稿/确认的申购单
            is_add = 'origin'
            if len(order_t) > 1:
                is_add = 'change'
            for spare in self.spare_parts_lines:
                has_record = False
                for line in order.line_id:
                    if line.bom_line_id.id == spare.id:
                        has_record = True
                if not has_record and not spare.has_purchase:
                    order.line_id.create({
                        'categ_id': spare.categ_id.id,
                        'product_id': spare.product_tmpl_id.product_variant_id.id,
                        'product_qty': spare.count * self.count,
                        'uom_id': spare.uom_id.id,
                        'brand_id': spare.brand_id.id,
                        'order_id': order.id,
                        'class_id': spare.class_categ_id.id,
                        'categ_class_id' : spare.class_id.id,
                        'bom_line_id': spare.id,
                        'is_add':is_add,
                        'material': spare.material
                    })
                    
        else:
            order = self.env['cowork.purchase.order'].search([('project_id','=',self.project_id.id),('state','=','purchase')])
            is_add = 'origin'
            if order:
                is_add = 'change'
            purchase = self.env['cowork.purchase.order'].create({
                'name': self.project_id.title,
                'user_id': self.env.user.id,
                'date': fields.Date.today(),
                # 'qty':1,
                'project_id': self.project_id.id,
            })
            if self.spare_parts_lines:
                for part in self.spare_parts_lines:
                    if part.has_purchase:
                        pass
                    else:
                        _logger.info("0000000000000")
                        _logger.info(is_add)
                        purchase.line_id.create({
                                'categ_id': part.categ_id.id,
                                'product_id': part.product_tmpl_id.product_variant_id.id,
                                'product_qty': part.count * self.count,
                                'uom_id': part.uom_id.id,
                                'brand_id': part.brand_id.id,
                                'order_id': purchase.id,
                                'class_id': part.class_categ_id.id,
                                'categ_class_id' : part.class_id.id,
                                'bom_line_id': part.id,
                                'is_add':is_add,
                                'material': part.material
                            })

    def action_to_cowork_purchase(self):
        order_line = self.env['cowork.purchase.order.line'].search([('project_id','=',self.project_id.id),('state','!=','cancel')]).mapped('id')
        return {
            'name': "申购明细",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'cowork.purchase.order.line',
            'views': [
                (self.env.ref('cowork_project_management_flow.view_tree_cowork_purchase_order_line').id, 'tree'),
            ],
            'domain': [('id', 'in', order_line)],
        }

    def action_to_cowork_purchase_fully(self):
        order_line = self.env['cowork.purchase.order.line'].search([('project_id','=',self.project_id.id),('state','!=','cancel')]).mapped('id')
        return {
            'name': "申购明细",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,graph,pivot',
            'res_model': 'cowork.purchase.order.line',
            'domain': [('id', 'in', order_line)],
        }

    def cowork_create(self):
        return {
            'name': "添加方案设计明细",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'material.wizard',
            'view_id': self.env.ref('cowork_project_management_flow.view_material_wizard_form').id,
            'target': 'new',
            'context': {
                    'default_bom_id': self.id,
                    'default_style': 'create'
            }
        }

    def button_approval(self):
        self.state = 'approval'

    def button_return(self):
        self.state = 'draft'

    def button_confirm(self):
        self.state = 'confirm'
    
    def button_to_return(self):
        self.state = 'approval'

class cowork_bom_material(models.Model):   #方案设计组件明细
    _name = 'cowork.bom.material'  

    bom_id = fields.Many2one("cowork.bom",string="物料方案")
    preliminary_scheme_id = fields.Many2one(comodel_name="cowork.quote.order",string="项目报价单",related="bom_id.name")
    name = fields.Char(string="组件名称")
    count = fields.Float(string="单台数量")
    class_id = fields.Many2one(comodel_name="cowork.material.class", string="类型")
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

class cowork_bom_material_part(models.Model):  #方案设计组件明细零部件
    _name = "cowork.bom.material.part"

    categ_id = fields.Many2one(comodel_name="product.category", string="名称")
    product_tmpl_id = fields.Many2one(comodel_name="product.template", string="规格")
    brand_id = fields.Many2one(comodel_name="product.brand", string="品牌")
    count = fields.Float(string="数量")
    comments = fields.Text(string="备注")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    material_id = fields.Many2one("cowork.bom.material",string="物料")
    bom_id = fields.Many2one("cowork.bom",string="方案设计")
    # bom_id_c = fields.Many2one("cowork.bom",string="更新物料方案")
    class_id = fields.Many2one("cowork.material.class",string="类型")
    class_categ_id = fields.Many2one("cowork.material.category",string="部门")
    has_purchase = fields.Boolean(default=False,string="是否转采购")
    default_code = fields.Char(string="产品编号",related='product_tmpl_id.default_code')
    material = fields.Char(string="材料")

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.uom_id = self.product_tmpl_id.uom_po_id or self.product_tmpl_id.uom_id

    def cowork_delete(self):
        order_line = self.env['cowork.purchase.order.line'].search([('bom_line_id','=',self.id),('state','in',('draft','confirm'))])
        if order_line:
            order_line.unlink()
        _logger.info("hashashashashas")
        
        tmp = ' '.join([
            self.categ_id.name if self.categ_id.name else '',
            self.product_tmpl_id.name if self.product_tmpl_id.name else '',
            self.brand_id.name if self.brand_id.name else '',
            str(self.count),
            self.uom_id.name if self.uom_id.name else '',
            self.class_id.name if self.class_id.name else '',
            self.class_categ_id.name if self.class_categ_id.name else ''
            ]) 
        _logger.info(tmp)
        message = self.bom_id.cowork_message_ids.create({
            'user_id': self.env.user.id,
            'date': fields.Datetime.now(),
            'operate': "明细删除，内容为：" + tmp,
            'bom_id': self.bom_id.id
        })
        _logger.info(message)
        self.unlink()

    def cowork_write(self):
        return {
            'name': "方案设计明细变更",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'material.wizard',
            'view_id': self.env.ref('cowork_project_management_flow.view_material_wizard_form').id,
            'target': 'new',
            'context': {
                    'default_style': 'write',
                    'default_categ_id': self.categ_id.id,
                    'default_product_tmpl_id': self.product_tmpl_id.id,
                    'default_brand_id': self.brand_id.id,
                    'default_count': self.count,
                    'default_comments': self.comments,
                    'default_uom_id': self.uom_id.id,
                    'default_material_id': self.material_id.id,
                    'default_bom_id': self.bom_id.id,
                    'default_class_id': self.class_id.id,
                    'default_class_categ_id': self.class_categ_id.id,
                    'default_material_part_id': self.id,
                    
                    'default_origin_categ_id': self.categ_id.id,
                    'default_origin_product_tmpl_id': self.product_tmpl_id.id,
                    'default_origin_brand_id': self.brand_id.id,
                    'default_origin_count': self.count,
                    'default_origin_comments': self.comments,
                    'default_origin_uom_id': self.uom_id.id,
                    'default_origin_class_id': self.class_id.id,
                    'default_origin_class_categ_id': self.class_categ_id.id,
            }
        }

class material_wizard(models.TransientModel):
    _name = 'material.wizard'

    categ_id = fields.Many2one(comodel_name="product.category", string="名称")
    product_tmpl_id = fields.Many2one(comodel_name="product.template", string="规格")
    brand_id = fields.Many2one(comodel_name="product.brand", string="品牌")
    count = fields.Float(string="数量")
    comments = fields.Text(string="备注")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="单位")
    material_id = fields.Many2one("cowork.bom.material",string="物料")
    material_part_id = fields.Many2one("cowork.bom.material.part",string="物料明细")
    bom_id = fields.Many2one("cowork.bom",string="方案设计")
    class_id = fields.Many2one("cowork.material.class",string="类型")
    class_categ_id = fields.Many2one("cowork.material.category",string="部门")

    origin_categ_id= fields.Many2one(comodel_name="product.category", string="名称")
    origin_product_tmpl_id= fields.Many2one(comodel_name="product.template", string="规格")
    origin_brand_id= fields.Many2one(comodel_name="product.brand", string="品牌")
    origin_count= fields.Float(string="数量")
    origin_comments= fields.Text(string="备注")
    origin_uom_id= fields.Many2one(comodel_name="uom.uom", string="单位")
    origin_class_id= fields.Many2one("cowork.material.class",string="类型")
    origin_class_categ_id= fields.Many2one("cowork.material.category",string="部门")

    style = fields.Selection([('create','创建'),('write','更改'),('delete','删除')])

    def action_to_confirm(self):
        if self.style == 'write':
            if self.material_part_id:
                order_line = self.env['cowork.purchase.order.line'].search([('bom_line_id','=',self.material_part_id.id)])
                if order_line:  #修改申购明细
                    if order_line.state == 'purchase':
                        raise UserError('已生成采购，请添加方案设计行')
                    else:
                        order_line.write({
                            'categ_class_id': self.class_id.id,
                            'class_id': self.class_categ_id.id,
                            'categ_id': self.categ_id.id,
                            'product_tmpl_id': self.product_tmpl_id.product_variant_id.id,
                            'brand_id': self.brand_id.id,
                            'product_qty': self.count * self.bom_id.count,#单台 x 数量
                            'uom_id': self.uom_id.id
                        })
                #修改bom明细+记录
                tmp = [
                        [self.origin_categ_id.name,self.categ_id.name],
                        [self.origin_product_tmpl_id.name,self.product_tmpl_id.name],
                        [self.origin_brand_id.name,self.brand_id.name],
                        [str(self.origin_count),str(self.count)],
                        [self.origin_uom_id.name,self.uom_id.name],
                        [self.origin_class_id.name,self.class_id.name],
                        [self.origin_class_categ_id.name,self.class_categ_id.name],
                        [self.origin_comments if self.origin_comments else '',self.comments if self.comments else '']
                    ]
                index = 0
                for t in tmp:
                    for i in t:
                        if not i:
                            i = ''
                    if t[0] != t[1]:
                        tmp[index] = " -> ".join(t)
                    index += 1
                
                index = 0
                while index < len(tmp):
                    if not isinstance(tmp[index],str):
                        tmp.pop(index)
                        _logger.info(tmp)
                    else:
                        index += 1
                        _logger.info(index)
                        _logger.info(len(tmp))

                self.bom_id.cowork_message_ids.create({
                    'user_id': self.env.user.id,
                    'date': fields.Datetime.now(),
                    'operate': "明细发生变动，内容为：\n\n" + "\n".join(tmp)
                })
                self.material_part_id.write({
                    'class_id': self.class_id.id,
                    'class_categ_id': self.class_categ_id.id,
                    'categ_id': self.categ_id.id,
                    'product_tmpl_id': self.product_tmpl_id.id,
                    'brand_id': self.brand_id.id,
                    'count': self.count,
                    'comments': self.comments,
                    'uom_id': self.uom_id.id
                })

        if self.style == 'create':
            comments = ''
            if self.comments:
                comments = self.comments
            self.bom_id.spare_parts_lines.create({
                'class_id': self.class_id.id,
                'class_categ_id': self.class_categ_id.id,
                'categ_id': self.categ_id.id,
                'product_tmpl_id': self.product_tmpl_id.id,
                'brand_id': self.brand_id.id,
                'count': self.count,
                'comments': self.comments,
                'uom_id': self.uom_id.id,
                'bom_id': self.bom_id.id
            })
            #记录新增信息
            comments = ''
            if self.comments:
                comments = self.comments
            self.bom_id.cowork_message_ids.create({
                'user_id': self.env.user.id,
                'date': fields.Datetime.now(),
                'operate': "新增 " +self.categ_id.name+' '+self.product_tmpl_id.name+' '+self.brand_id.name+' '+str(self.count)+' '+self.uom_id.name+' '+self.class_id.name+' '+self.class_categ_id.name+' '+comments
            })
            # purchase = self.env['cowork.purchase.order'].search([('project_id', '=',self.bom_id.project_id.id)])
            # if purchase:
            #     pur_lst = []
            #     for p in purchase:
            #         if p.state in ['draft','confirm']:
            #             pur_lst.append(p)
            #     if len(pur_lst) == 0:
            #         _logger.info("需另外申购")
            #     else:
            #         purchase = pur_lst[-1]
            #         purchase.line_id.create({
            #             'categ_class_id': self.class_id.id,
            #             'class_id': self.class_categ_id.id,
            #             'categ_id': self.categ_id.id,
            #             'product_tmpl_id': self.product_tmpl_id.product_variant_id.id,
            #             'brand_id': self.brand_id.id,
            #             'product_qty': self.count,
            #             'uom_id': self.uom_id.id,
            #             'order_id':purchase.id
            #         })