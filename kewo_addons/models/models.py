# -*- coding: utf-8 -*-

from odoo import models, fields, api

class apply_for(models.Model):
    _name = 'apply.for'

    name = fields.Char(u'name')

class kewo_sale(models.Model):
    _name = 'kewo.sale'

    name = fields.Char(u'名称')