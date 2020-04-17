# -*- coding: utf-8 -*-

from odoo import models, fields, api

class cowork_project_technical(models.Model):
    _name = 'cowork.project.technical'
    _description = u'技术参数'

    # efficiency_beat = fields.Float(string="效率节拍")
    # robot_model_id = fields.Many2one(comodel_name="product.product", string="机器人型号")
    # robot_count = fields.Float(u'机器人数量')
    # plc_controller = fields.Many2one(comodel_name="product.product", string="PLC控制器")
    # plc_controller_count = fields.Float(u'PLC控制器数量')
    # module = fields.Many2one(comodel_name="product.product", string="模组")
    # module_count = fields.Float(u'模组数量')
    # sensor = fields.Many2one(comodel_name="product.product", string="传感器")
    # sensor_count = fields.Float(u'传感器数量')
    # cylinder = fields.Many2one(comodel_name="product.product", string="气缸")
    # cylinder_count = fields.Float(u'气缸数量')
    # fixture = fields.Many2one(comodel_name="product.product", string="治具")
    # fixture_count = fields.Float(u'治具数量')
    # motor = fields.Many2one(comodel_name="product.product", string="电机配置")
    # motor_count = fields.Float(u'电机数量')
    # ccd_vision = fields.Many2one(comodel_name="product.product", string="CCD视觉")
    # ccd_vision_count = fields.Float(u'CCD视觉数量')
    # pneumatic_components = fields.Many2one(comodel_name="product.product", string="气动元件")
    # pneumatic_components_count = fields.Float(u'气动元件数量')
    type = fields.Selection([(
        ('robot_model_id',u'机器人型号'),
        ('plc_controller',u'PLC控制器'),
        ('module',u'模组'),
        ('sensor',u'传感器'),
        ('cylinder',u'气缸'),
        ('fixture',u'治具'),
        ('motor',u'电机配置'),
        ('ccd_vision',u'CCD视觉'),
        ('pneumatic_components',u'气动元件')
    )],string="类型")
    count = fields.Float(u'数量')
    product_id = fields.Many2one('product.product',string="物料")

    technical_id = fields.Many2one("cowork.technical.analysis",string="技术分析单")