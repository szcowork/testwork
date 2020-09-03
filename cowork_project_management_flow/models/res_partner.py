# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    project_no = fields.Integer(string='立项数量', compute='_compute_project_ids')
    material_class_id = fields.Many2many("cowork.material.class",string="供应商类型")

    @api.multi
    def _compute_project_ids(self):
        for record in self:
            partner = self.env['cowork.project.apply'].search(
                [('partner_id', '=', record.id)])
            if partner:
                record.project_no = len(partner)

    @api.multi
    def action_view_project(self):
        action = {
            'name': '立项记录',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'cowork.project.apply',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.id)],
        }
        return action

class hr_job(models.Model):
    _inherit = 'hr.job'

    unit_price = fields.Float(string="项目人力成本单价(元/h)")