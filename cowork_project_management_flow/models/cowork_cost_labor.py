# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class cowork_cost_labor(models.Model):
    _name = "cowork.cost.labor"
    _description = "人力成本行"
    

    preliminary_scheme_id = fields.Many2one(comodel_name="cowork.scheme.preliminary", ondelete="cascade", string="项目初步方案")
    job_id = fields.Many2one(comodel_name="hr.job", required=True, string="岗位")
    count = fields.Integer(default=1, string="人数")
    hours_per_day = fields.Float(default=8, string="工时/天")
    count_day = fields.Float(default=1, string="工作天数")
    total_hours = fields.Float(string="工时(h)")
    unit_price = fields.Monetary(string="单价(元/h)")
    total_price = fields.Monetary(string="总价")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")

    @api.onchange('count','hours_per_day','count_day','job_id')  #,'unit_price'
    def _compute_cost(self):
        if self.job_id:
            if self.job_id.unit_price > 0.0:
                self.unit_price = self.job_id.unit_price

                self.total_hours = self.count * self.hours_per_day * self.count_day
                self.total_price = self.total_hours * self.job_id.unit_price   #self.unit_price
            else:
                raise UserError("请配置该岗位人员人力成本单价信息！")

    def trans_quote(self, quote):
        self.env['cowork.cost.labor.quote'].create({
            'quote_id': quote.id,
            'job_id':self.job_id.id,
            'count':self.count,
            'hours_per_day':self.hours_per_day,
            'count_day':self.count_day,
            'total_hours':self.total_hours,
            'unit_price':self.unit_price,
            'total_price':self.total_price,
            'currency_id':self.currency_id.id,
        })