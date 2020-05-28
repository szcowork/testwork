# -*- coding: utf-8 -*-

from odoo import models, fields, api


class cowork_cost_labor(models.Model):
    _name = "cowork.cost.labor.quote"
    _description = "人力成本行"

    job_id = fields.Many2one(comodel_name="hr.job", required=True, string="岗位")
    count = fields.Integer(default=1, string="人数")
    hours_per_day = fields.Float(default=8, string="工时/天")
    count_day = fields.Float(default=1, string="工作天数")
    total_hours = fields.Float(string="工时(h)")
    unit_price = fields.Monetary(string="单价(元/h)")
    total_price = fields.Monetary(string="总价")
    unit_quote = fields.Monetary(string='单台报价')
    total_quote = fields.Monetary(string='总报价')
    quote_id = fields.Many2one(comodel_name="cowork.quote.order", ondelete="cascade", string="项目报价单")
    currency_id = fields.Many2one(comodel_name="res.currency", default=lambda self: self.env.user.company_id.currency_id, string="货币")
    work_info_ids = fields.One2many("work.info","line_id",string="工作内容")

    state = fields.Selection([
        ('business','商务部'),
        ('technology','技术部'),
        ('project','项目管理部'),
        ('deputy','副总经理'),
        ('general','总经理'),
        ('cancel','无效')
    ],string="状态",related='quote_id.state')

    @api.onchange('count','hours_per_day','count_day','unit_price')
    def _compute_cost(self):
        self.total_hours = self.count * self.hours_per_day * self.count_day
        self.total_price = self.total_hours * self.unit_price

    def edit_spare_parts(self):
        return {
            'name': "-".join([self.job_id.name, self.quote_id.name]) if self.job_id else self.quote_id.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cowork.cost.labor.quote',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
            'view_id':self.env.ref('cowork_project_management_flow.view_form_cowork_cost_labor_quote').id,
            'context':{
                'form_view_initial_mode':'edit'
            }
        }

class work_info(models.Model):
    _name = 'work.info'

    line_id = fields.Many2one("cowork.cost.labor.quote",string="人力成本行")
    job_id = fields.Many2one("job.duty",string="名称")
    brand_id = fields.Many2one("product.brand",string="品牌")
    uom_id = fields.Many2one("uom.uom",string="单位")
    count = fields.Float("数量")

class job_duty(models.Model):
    _name = "job.duty"

    name = fields.Char("名称")