# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cowork_project_technical(models.Model):
    _name = 'cowork.project.technical'
    _description = u'技术参数'
    
    categ_id = fields.Many2one(comodel_name="product.category", string="物料类别")    

    count = fields.Float(u'数量')
    product_id = fields.Many2one('product.product',string="物料")

    technical_id = fields.Many2one("cowork.technical.analysis",string="技术分析单")
    
    type = fields.Selection([
        ('robot_model_id',u'机器人型号'),
        ('plc_controller',u'PLC控制器'),
        ('module',u'模组'),
        ('sensor',u'传感器'),
        ('cylinder',u'气缸'),
        ('fixture',u'治具'),
        ('motor',u'电机配置'),
        ('ccd_vision',u'CCD视觉'),
        ('pneumatic_components',u'气动元件')
    ],string="类型")