# -*- coding: utf-8 -*-

from odoo import models, fields, api

class supplier_approval(models.Model):
    _name = "supplier.approval"
    _description = "供应商审批"
    _inherit = ['mail.thread']
    
    name = fields.Char(required=True, string="名称")
    vat = fields.Char(string="税号")
    phone = fields.Char(string="电话")
    mobile = fields.Char(string="手机")
    country_id = fields.Many2one(comodel_name="res.country", string="国家/地区")
    state_id = fields.Many2one(comodel_name="res.country.state", string="省/州")
    city = fields.Char(string="城市")
    email = fields.Char(string="email")
    website = fields.Char(string="网站")
    state = fields.Selection([('draft','草稿'),('approval','审批中'),('pass','已通过'),('cancel','取消')],default='draft',string="状态")
    material_class_id = fields.Many2many("cowork.material.class",string="供应商类型")
    aptitute = fields.One2many("supplier.aptitute","approval_id",string="资质")
    street = fields.Char(string="街道")
    zip = fields.Char(string="邮编")
    partner_id = fields.Many2one("res.partner",string="供应商")
    
    def button_approval(self):
        self.state = 'approval'

    def button_draft(self):
        self.state = 'draft'

    def button_cancel(self):
        self.state = 'cancel'

    def button_to_pass(self):
        self.state = 'pass'
        country = False
        if self.country_id:
            country = self.country_id.id
        state_id = False
        if self.state_id:
            state_id = self.state_id.id

        materials = []
        if self.material_class_id:
            for material in self.material_class_id:
                materials.append(material.id)

        partner = self.env['res.partner'].create({
            'name': self.name,
            'vat': self.vat,
            'phone': self.phone,
            'mobile': self.mobile,
            'country_id': country,
            'state_id': state_id,
            'city': self.city,
            'email': self.email,
            'website': self.website,
            'material_class_id': [(6,0,materials)],
            'street': self.street,
            'zip': self.zip,
            'supplier':True,
            'customer': False
        })
        self.partner_id = partner.id

class supplier_aptitute(models.Model):
    _name = 'supplier.aptitute'
    _description = '供应商资质'

    name = fields.Char(string="名称")
    file = fields.Binary(string="文件")
    approval_id = fields.Many2one("supplier.approval",string="供应商审核")