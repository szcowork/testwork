# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = "product.product"


    technical_confirmation_set_sale_count = fields.Float(string="数量" ,compute='_compute_sale_count')
    technical_confirmation_set_purchase_count = fields.Float(string="数量" ,compute='_compute_purchase_count')
    
    def _compute_sale_count(self):
        for record in self:
            technical_confirmation_id = self.env.context.get('technical_confirmation_id')
            if technical_confirmation_id:
                technical_confirmation = self.env['technical.confirmation'].browse([technical_confirmation_id])[0]
                flag = False
                for item in technical_confirmation.pre_sale_line:
                    if item.product_id.id == record.id:
                        _logger.info(item.product_qty)
                        flag = True
                        record.technical_confirmation_set_sale_count = item.product_qty
                if flag == False:
                    record.technical_confirmation_set_sale_count = 1.0


    def _compute_purchase_count(self):
        for record in self:
            technical_confirmation_id = self.env.context.get('technical_confirmation_id')
            if technical_confirmation_id:
                technical_confirmation = self.env['technical.confirmation'].browse([technical_confirmation_id])[0]
                flag = False
                for item in technical_confirmation.pre_purchase_line:
                    if item.product_id.id == record.id:
                        _logger.info(item.product_qty)
                        flag = True
                        record.technical_confirmation_set_purchase_count = item.product_qty
                if flag == False:
                    record.technical_confirmation_set_purchase_count = 1.0

    @api.multi
    def button_sale_count(self):
        self.ensure_one()
        _logger.info('button_sale_count') 
        active_id = self.env.context.get('active_id')
        _logger.info(active_id)
        technical_confirmation_id = self.env.context.get('technical_confirmation_id')
        technical_confirmation = self.env['technical.confirmation'].browse([technical_confirmation_id])[0]
        items = technical_confirmation.pre_sale_line
        flag = False
        tem_id = 0
        for item in items:
            if active_id == item.product_id.id:
                flag = True
                tem_id = item.id
        if flag:
            _logger.info('123')
            return {
                'name': "数量",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'presale.line',
                'res_id': tem_id,
                'target': 'new',
            }
        else:
            _logger.info('456')
            product_id = self.env['product.product'].browse([active_id])[0]
            presale_line_id = self.env['presale.line'].create({'product_id':active_id,'product_qty':1.0,'tc_order_id':technical_confirmation_id,'product_uom':product_id.uom_id.id})
            technical_confirmation.write({'pre_sale_line':[(4, presale_line_id.id, 0)]})
            return {
                'name': "数量",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'presale.line',
                'res_id': presale_line_id.id,
                'target': 'new',
            }



    @api.multi
    def button_purchase_count(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        technical_confirmation_id = self.env.context.get('technical_confirmation_id')
        technical_confirmation = self.env['technical.confirmation'].browse([technical_confirmation_id])[0]
        items = technical_confirmation.pre_purchase_line
        flag = False
        tem_id = 0
        for item in items:
            if active_id == item.product_id.id:
                flag = True
                tem_id = item.id 
        if flag:
            _logger.info('123')
            return {
                'name': "数量",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'prepurchase.line',
                'res_id': tem_id,
                'target': 'new',
            }
        else: 
            _logger.info('456')
            product_id = self.env['product.product'].browse([active_id])[0]
            prepurchase_line_id = self.env['prepurchase.line'].create({'product_id':active_id,'product_qty':1.0,'tc_order_id':technical_confirmation_id,'product_uom':product_id.uom_id.id})
            technical_confirmation.write({'pre_purchase_line':[(4, prepurchase_line_id.id, 0)]})
            return {
                'name': "数量",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'presale.line',
                'res_id': prepurchase_line_id.id,
                'target': 'new',
            }

    @api.multi
    def button_bom_list(self):
        self.ensure_one()
        _logger.info('add_field_to_view')
        _logger.info(self.env.context)
        active_id = self.env.context.get('active_id')
        _logger.info(active_id)
        product = self.env['product.product'].browse([active_id])[0]
        _logger.info(product.product_tmpl_id)
        bom_ids = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
        ]).mapped('id')
        if len(bom_ids) == 0 :
            bom_id = self.env['mrp.bom'].create({'product_tmpl_id':product.product_tmpl_id.id})
            # self.technical_order = tc_id.id
            return {
                'name': "BOM",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mrp.bom',
                'res_id': bom_id.id,
                'target': 'new',
            }
        elif len(bom_ids) == 1 :
            return {
                'name': "BOM",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mrp.bom',
                'res_id': bom_ids[0],
                'target': 'new',
            }
        else:
            return {
                'name': "BOM",
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'res_model': 'technical.confirmation',
                'domain': [('id', 'in', bom_ids)],
                'target': 'new',
            }
