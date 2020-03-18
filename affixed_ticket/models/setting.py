# -*- encoding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)
from odoo import models, fields, api
from datetime import datetime, timedelta

class TicketSettingWizard(models.TransientModel):
    _name = 'affixed.ticket.settings'
    _description = u'基本设置'
    _inherit = 'res.config.settings'


    # bank_rate = fields.Float(u'自有资金年化利率(%)')            
    bank_day = fields.Integer(u'自有资金年日数')
    out_day = fields.Integer(u'外部资金年日数',default=360)
    first_crash = fields.Monetary(u'首次资金余额')
    first_ticket = fields.Monetary(u'首次票据余额')
    active_zidong = fields.Boolean(u'激活自动化')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
        default=lambda self: self.env.user.company_id.currency_id.id)

    # journal = fields.Many2one("account.journal",u'日记账')
    template = fields.Many2one("account.move.template",u'凭证模板')
    # jie = fields.Many2one("account.account",u'借方科目')
    # dai = fields.Many2one("account.account",u'贷方科目')
    # jie_1 = fields.Many2one("account.account",u'借方科目')
    # dai_1 = fields.Many2one("account.account",u'贷方科目')
    template_1 = fields.Many2one("account.move.template",u'凭证模板')

    @api.model
    def get_values(self):
        res = super(TicketSettingWizard, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        # _logger.info(params.get_param('affixed_ticket.active_zidong'))
        res.update(
            bank_day=int(params.get_param('affixed_ticket.bank_day', default=365)),
            out_day=int(params.get_param('affixed_ticket.out_day', default=360)),
            first_crash=float(params.get_param('affixed_ticket.first_crash')),
            first_ticket=float(params.get_param('affixed_ticket.first_ticket')),
            active_zidong=params.get_param('affixed_ticket.active_zidong'),
            # jie=int(params.get_param('affixed_ticket.jie')),
            # jie_1=int(params.get_param('affixed_ticket.jie_1')),
            # dai=int(params.get_param('affixed_ticket.dai')),
            # dai_1=int(params.get_param('affixed_ticket.dai_1')),
            # journal=int(params.get_param('affixed_ticket.journal')),
            template=int(params.get_param('affixed_ticket.template')),
            template_1=int(params.get_param('affixed_ticket.template_1')),
        )
        return res
    @api.multi
    def set_values(self):
        super(TicketSettingWizard, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.bank_day", self.bank_day)
        self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.out_day", self.out_day)
        self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.first_crash", self.first_crash)
        self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.first_ticket", self.first_ticket)
        self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.active_zidong", self.active_zidong)
        # self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.jie", self.jie.id)
        # self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.jie_1", self.jie_1.id)
        # self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.dai_1", self.dai_1.id)
        # self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.dai", self.dai.id)
        # self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.journal", self.journal.id)
        self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.template", self.template.id)
        self.env['ir.config_parameter'].sudo().set_param("affixed_ticket.template_1", self.template_1.id)
        if self.active_zidong:
            active = self.env.ref('affixed_ticket.ticket_ircron_action').id
            cron = self.env['ir.cron'].search([('id','=',active),('active','=',False)])
            date = fields.Date.today()
            detaday=timedelta(days=1)
            date = date + detaday
            date = str(date) + " 10:00:00"
            date = datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
            if cron:
                cron.write({
                    # 'active':True,
                    'nextcall':date
                })
                cron.active = not cron.active
        else:
            active = self.env.ref('affixed_ticket.ticket_ircron_action').id
            cron = self.env['ir.cron'].search([('id','=',active)])
            if cron:
                cron.active = not cron.active