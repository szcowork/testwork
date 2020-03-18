# -*- coding: utf-8 -*-

from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class affixed_ticket(models.Model):
    _name = 'affixed.ticket'
    _description = u'贴票业务'

    partner = fields.Many2one('res.partner', u'客户')
    saler = fields.Many2one('res.partner', u'客户经理')
    company = fields.Many2one('res.company', u'收票主体')
    name = fields.Char(u'票据号')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    plandays = fields.Integer(u'票据剩余天数', compute="compute_costs")
    othercost = fields.Monetary(u'其他成本')
    buycost = fields.Monetary(u'购票支付金额', compute="compute_costs", store=True)

    daycost = fields.Monetary(u'支付资金每日成本', compute="compute_costs")
    planprofit = fields.Monetary(u'购票总收入', compute="compute_costs")
    everyday_income = fields.Monetary(u'持票每日收入', compute="compute_costs")
    planprofit_true = fields.Monetary(u'持有到期利润', compute="compute_costs")
    avedayprofit = fields.Monetary(u'持票每日利润', compute="compute_costs")

    holdday = fields.Integer(u'实际持票天数', compute="compute_costs")
    holdprofit = fields.Monetary(
        u'持票期间实际利润', compute="compute_costs", store=True)

    hold_no = fields.Integer(u'持票数', compute='_compute_hold_ids')
    atype = fields.Boolean(u'是否再贴现', default=False)

    sell_date = fields.Date(u'再贴现日期')
    sell_rate = fields.Float(u'再贴现年化利率(%)', compute='compute_costs')

    sell_day = fields.Integer(u'再贴现天数', compute="compute_costs")
    sell_money = fields.Monetary(
        u'再贴现收款金额', compute="compute_costs", store=True)
    sell_money_true = fields.Monetary(u'再贴现实际收款金额')
    sell_total = fields.Monetary(u'再贴现总收入', compute="compute_costs")
    sell_cost = fields.Monetary(u'再贴现成本', compute="compute_costs")
    # true_profit = fields.Monetary(u'实际毛利润',compute="compute_costs")
    true_profit_true = fields.Monetary(
        u'实际利润', compute="compute_costs", store=True)
    sell_profit = fields.Monetary(
        u'再贴现利润', compute="compute_costs", store=True)

    amount = fields.Monetary(u'票面金额')
    disscount_rate = fields.Float(u'收票年化利率(%)', default=12.0)
    bank_rate = fields.Float(u'自有资金年化利率(%)', default=6.0)
    buy_date = fields.Date(u'收票日期')  # 贴现日
    amount_date = fields.Date(u'票据到期日')

    state = fields.Selection([
        ('draft', u'草稿'),
        ('hold', u'持票中'),
        ('pay', u'兑付'),
        ('error', u'异常'),
        ('buy', u'再贴现')
    ], u'状态', default='draft', readonly=True)

    delay_day = fields.Integer(u'实际延迟天数（考虑票据到期处于节假日）')
    delay_cost = fields.Monetary(
        u'实际延迟成本', compute="compute_costs", store=True)

    bank_day = fields.Float(u'自有资金年日数', compute="compute_costs", store=True)
    out_day = fields.Float(u'外部资金年日数', compute="compute_costs", store=True)

    maker = fields.Many2one("res.partner", u'出票人')
    accept = fields.Many2one("res.partner", u'承兑人')  # ,related='maker'
    make_date = fields.Date(u'出票日期')

    # accept_date = fields.Date(u'收票日期')
    # _compute_daily_financial
    ticket_rate = fields.Float(u'票面利率(未税)%', compute="compute_costs")
    account = fields.Boolean(u'是否开票')
    ticket_rate_tax = fields.Float(
        u'票面利率(含税)%', compute="compute_costs")  # _compute_daily_financial
    # have_total_income = fields.Monetary(u'收票总收入')
    tax = fields.Monetary(u'税', compute="compute_costs")
    money_from = fields.Many2one("res.company", u'资金来源')
    account_move = fields.Binary(u'收票凭证')
    # picture = fields.Binary(u'图像', attachment=True)
    sell_move = fields.Binary(u'兑付凭证')
    buy_move = fields.Binary(u'再贴现凭证')

    hold_total_day = fields.Integer(u'持票累计天数')  # _compute_daily_financial
    hold_total_income = fields.Monetary(u'持票累计收入')
    hold_total_cost = fields.Monetary(u'持票累计成本')
    hold_total_profit = fields.Monetary(u'持票累计利润')

    invoice_no = fields.Integer(
        compute='_compute_invoice_ids', string=u'凭证数')

    move_ids = fields.One2many("account.move", "ticket", string=u"凭证行")

    # @api.model
    # def create(self, vals):
        # res = super(affixed_ticket, self).create(vals)
        # if res.amount_date < fields.Date.today():
        #     if res.sell_date:
        #         day = (res.sell_date - res.buy_date).days
        #         res.hold_total_day = day
        #         res.hold_total_cost = res.daycost * day
        #         res.hold_total_income = res.everyday_income * day
        #         res.hold_total_profit = res.avedayprofit * day
        #     else:
        #         day = (res.amount_date - res.buy_date).days
        #         res.hold_total_day = day
        #         res.hold_total_cost = res.daycost * day
        #         res.hold_total_income = res.everyday_income * day
        #         res.hold_total_profit = res.avedayprofit * day
        # else:
        #     if res.sell_date:
        #         day = (res.sell_date - res.buy_date).days
        #         res.hold_total_day = day
        #         res.hold_total_cost = res.daycost * day
        #         res.hold_total_income = res.everyday_income * day
        #         res.hold_total_profit = res.avedayprofit * day
        #     else:
        #         day = (fields.Date.today() - res.buy_date).days
        #         res.hold_total_day = day
        #         res.hold_total_cost = res.daycost * day
        #         res.hold_total_income = res.everyday_income * day
        #         res.hold_total_profit = res.avedayprofit * day
        # return res

    @api.one
    @api.depends("amount", "disscount_rate", "buy_date", "sell_date", "bank_rate", "amount_date", "atype", "delay_day", "sell_money_true", "account")
    def compute_costs(self):
        # 获取外部自今年日数
        # _logger.info(self.bank_day)
        # _logger.info(self.out_day)
        if self.bank_day and self.out_day:
            bank_day = self.bank_day
            out_day = self.out_day
        else:
            config = self.env["ir.config_parameter"]
            bank_day = float(config.get_param('affixed_ticket.bank_day'))
            self.bank_day = bank_day
            out_day = float(config.get_param('affixed_ticket.out_day'))
            self.out_day = out_day

        if self.amount_date and self.buy_date:
            if self.amount_date <= self.buy_date:
                raise ValidationError(u'收票日期需小于票据到期日')
            else:
                plandays = (self.amount_date - self.buy_date).days

            self.plandays = plandays  # 票据剩余天数

            if self.amount and self.disscount_rate and self.bank_rate:
                buycost = self.amount * \
                    (1-self.disscount_rate/100*plandays/out_day)
                self.buycost = buycost  # 购票支付金额

                daycost = buycost*self.bank_rate/100/bank_day
                self.daycost = daycost  # 支付资金每日成本

                planprofit = self.amount - buycost
                self.planprofit = planprofit  # 购票总收入

                self.ticket_rate = planprofit / self.amount * 100.0
                self.ticket_rate_tax = 1.068 * planprofit / self.amount * 100.0
                if self.account:
                    self.tax = self.ticket_rate_tax * planprofit / 100.0
                else:
                    self.tax = self.ticket_rate * planprofit / 100.0

                everyday_income = planprofit / plandays
                self.everyday_income = everyday_income  # 持票每日收入

                avedayprofit = everyday_income - daycost  # planprofit_true / plandays
                self.avedayprofit = avedayprofit  # 持票每日利润

                planprofit_true = plandays * avedayprofit  # planprofit - daycost*plandays
                self.planprofit_true = planprofit_true  # 计划利润
                self.true_profit_true = planprofit_true

                self.delay_cost = self.delay_day * daycost  # 实际延迟成本
                if self.atype == False:
                    self.holdday = plandays
                else:
                    if self.sell_date and self.sell_money_true:
                        if self.sell_date > self.amount_date:
                            raise ValidationError(u'再贴现日期需小于票据到期日')
                        else:
                            # self.state = 'pay'
                            self.delay_cost = 0  # 无实际延迟成本
                            self.holdday = (self.sell_date -
                                            self.buy_date).days
                        sell_day = (self.amount_date - self.sell_date).days
                        self.sell_day = sell_day  # 再贴现天数
                        sell_total = sell_day*everyday_income  # 再贴现总收入
                        self.sell_total = sell_total
                        sell_cost = self.amount - self.sell_money_true
                        self.sell_cost = sell_cost  # 再贴现成本

                        sell_rate = (1 - self.sell_money_true /
                                     self.amount)*out_day/float(sell_day)*100
                        self.sell_rate = sell_rate

                        sell_money = self.amount * \
                            (1 - sell_day/out_day*self.sell_rate/100)
                        self.sell_money = sell_money  # 再贴现收款金额
                        # true_profit = sell_money - buycost
                        # self.true_profit = true_profit #实际毛利润
                        # true_profit_true - self.holdday * avedayprofit
                        sell_profit = sell_total - sell_cost
                        self.sell_profit = sell_profit  # 再贴现利润
                        true_profit_true = sell_profit + self.holdday * \
                            avedayprofit  # true_profit - self.holdday * daycost
                        self.true_profit_true = true_profit_true  # 实际利润
                    else:
                        self.holdday = plandays

                holdprofit = self.holdday * avedayprofit
                self.holdprofit = holdprofit  # 持票期间实际利润
                if self.amount_date < fields.Date.today():
                    if self.sell_date:
                        day = (self.sell_date - self.buy_date).days
                        self.hold_total_day = day
                        self.hold_total_cost = daycost * day
                        self.hold_total_income = everyday_income * day
                        self.hold_total_profit = avedayprofit * day
                    else:
                        day = (self.amount_date - self.buy_date).days
                        self.hold_total_day = day
                        self.hold_total_cost = daycost * day
                        self.hold_total_income = everyday_income * day
                        self.hold_total_profit = avedayprofit * day
                else:
                    if self.sell_date:
                        day = (self.sell_date - self.buy_date).days
                        self.hold_total_day = day
                        self.hold_total_cost = daycost * day
                        self.hold_total_income = everyday_income * day
                        self.hold_total_profit = avedayprofit * day
                    else:
                        day = (fields.Date.today() - self.buy_date).days
                        self.hold_total_day = day
                        self.hold_total_cost = daycost * day
                        self.hold_total_income = everyday_income * day
                        self.hold_total_profit = avedayprofit * day

    # @api.multi
    # def write(self, vals):
        # res = super(affixed_ticket, self).write(vals)
        # totoday = fields.Date.today()
        # day = (totoday - self.buy_date).days
        # _logger.info(totoday)
        # _logger.info(day)
        # _logger.info("211121212121")
        # _logger.info(vals)
        # _logger.info(self.daycost)
        # if self.state == 'draft':
        #     # vals.create()
        #     if vals.get('buy_day'):
        #         plandays = (self.amount_date - vals['buy_date']).days
        #         buycost = self.amount * \
        #             (1-self.disscount_rate/100*plandays/out_day)
        #         self.buycost = buycost  # 购票支付金额

        #         daycost = buycost*self.bank_rate/100/bank_day
        #         self.daycost = daycost  # 支付资金每日成本
            # self.compute_costs()
            # _logger.info(self.amount_date)

            # if self.amount_date < fields.Date.today():
            #     if self.sell_date:
            #         day = (self.sell_date - self.buy_date).days
            #         vals['hold_total_day'] = day
            #         vals['hold_total_cost'] = self.daycost * day
            #         vals['hold_total_income'] = self.everyday_income * day
            #         vals['hold_total_profit'] = self.avedayprofit * day
            #     else:
            #         day = (self.amount_date - self.buy_date).days
            #         vals['hold_total_day'] = day
            #         vals['hold_total_cost'] = self.daycost * day
            #         vals['hold_total_income'] = self.everyday_income * day
            #         vals['hold_total_profit'] = self.avedayprofit * day
            # else:
            #     if self.sell_date:
            #         day = (self.sell_date - self.buy_date).days
            #         vals['hold_total_day'] = day
            #         vals['hold_total_cost'] = self.daycost * day
            #         vals['hold_total_income'] = self.everyday_income * day
            #         vals['hold_total_profit'] = self.avedayprofit * day
            #     else:
            #         _logger.info("4444444444444")
            #         _logger.info(self.hold_total_day)
            #         day = (fields.Date.today() - self.buy_date).days
            #         vals['hold_total_day'] = day
            #         _logger.info(day)
            #         # self.hold_total_day = day
            #         # self.hold_total_day = day
            #         # _logger.info(self.hold_total_day)
            #         _logger.info("3333333333333")
            #         vals['hold_total_cost'] = self.daycost * day
            #         vals['hold_total_income'] = self.everyday_income * day
            #         vals['hold_total_profit'] = self.avedayprofit * day

        # return super(affixed_ticket, self).write(vals)

    @api.onchange("maker")
    def onchange_accept(self):
        if self.accept.id == False:
            self.accept = self.maker

    @api.onchange("partner")
    def onchange_saler(self):
        if self.saler.id == False:
            partner = self.env['affixed.ticket'].search(
                [('partner', '=', self.partner.id)])
            if len(partner) > 0:
                self.saler = partner[-1].saler

    @api.onchange("sell_money")
    def onchange_sell_money_true(self):
        if self.sell_money_true == 0:
            self.sell_money_true = self.sell_money

    @api.multi
    def _compute_hold_ids(self):
        for order in self:
            hold = self.env['ticket.info'].search(
                [('state', '=', 'hold'), ('ticket', '=', self.id)])
            if hold:
                order.hold_no = len(hold)

    @api.multi
    def action_view_hold(self):
        action = {
            'name': u'每日明细',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ticket.info',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('ticket', '=', self.id)],
        }
        return action

    @api.multi
    def _compute_invoice_ids(self):
        for order in self:
            invoice = self.env['account.move'].search(
                [('ticket', '=', self.id)])
            if invoice:
                order.invoice_no = len(invoice)

    @api.multi
    def action_view_invoice(self):
        action = {
            'name': u'会计凭证',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('ticket', '=', self.id)],
        }
        return action

    @api.one
    def buy_account_move(self):  # 购票凭证
        config = self.env["ir.config_parameter"]
        template = config.get_param('affixed_ticket.template')

        if template == False:
            raise ValidationError(u'请在设置中选择凭证模板')
        else:
            template = int(template)

        sub = self.env['account.move.template'].search([('id', '=', template)])

        move = self.env['account.move'].sudo().create({
            'date': self.buy_date,
            'ref': self.name,
            'company_id': self.company.id,
            'journal_id': sub.journal_id.id,
            'ticket': self.id
        })

        if sub.lines:
            for l in sub.lines:
                if l.value == 'fixed':
                    if l.att == 'debit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '购票',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': self[l.field.name],
                            'credit': 0.0
                        })
                    if l.att == 'credit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '购票',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': 0.0,
                            'credit': self[l.field.name]
                        })
                if l.value == 'code':
                    localdict = {}
                    for f in l.field_ids:
                        localdict[f.name] = self[f.name]
                    safe_eval(l.code, localdict, mode="exec", nocopy=True)
                    if l.att == 'debit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '购票',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': localdict['result'],
                            'credit': 0.0
                        })
                    if l.att == 'credit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '购票',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': 0.0,
                            'credit': localdict['result']
                        })

        # return {
        #     'name': u'会计凭证',
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'account.move',
        #     'res_id': move.id,
        #     'view_id': self.env.ref('account.view_move_form').id,
        #     # 'flags': {'initial_mode': 'edit'},
        #     # 'context': {
        #     #     'default_date':self.buy_date,
        #     #     'default_ref':self.name,
        #     #     'default_company_id':self.company.id,
        #     #     'default_journal_id':journal,
        #     #     # 'default_rooms':self.rooms.id,
        #     # }
        # }

    @api.one
    def sell_account_move(self):  # 到期兑付
        config = self.env["ir.config_parameter"]
        template = config.get_param('affixed_ticket.template_1')

        if template == False:
            raise ValidationError(u'请在设置中选择凭证模板')
        else:
            template = int(template)

        sub = self.env['account.move.template'].search([('id', '=', template)])

        move = self.env['account.move'].sudo().create({
            'date': self.buy_date,
            'ref': self.name,
            'company_id': self.company.id,
            'journal_id': sub.journal_id.id,
            'ticket': self.id
        })

        if sub.lines:
            for l in sub.lines:
                if l.value == 'fixed':
                    if l.att == 'debit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '到期兑付',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': self[l.field.name],
                            'credit': 0.0
                        })
                    if l.att == 'credit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '到期兑付',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': 0.0,
                            'credit': self[l.field.name]
                        })
                if l.value == 'code':
                    localdict = {}
                    for f in l.field_ids:
                        localdict[f.name] = self[f.name]
                    safe_eval(l.code, localdict, mode="exec", nocopy=True)
                    if l.att == 'debit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '到期兑付',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': localdict['result'],
                            'credit': 0.0
                        })
                    if l.att == 'credit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '到期兑付',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': 0.0,
                            'credit': localdict['result']
                        })

    @api.one
    def selling_account_move(self):  # 再贴现
        config = self.env["ir.config_parameter"]
        template = config.get_param('affixed_ticket.template_1')

        if template == False:
            raise ValidationError(u'请在设置中选择凭证模板')
        else:
            template = int(template)

        sub = self.env['account.move.template'].search([('id', '=', template)])

        move = self.env['account.move'].sudo().create({
            'date': self.buy_date,
            'ref': self.name,
            'company_id': self.company.id,
            'journal_id': sub.journal_id.id,
            'ticket': self.id
        })

        if sub.lines:
            for l in sub.lines:
                if l.value == 'fixed':
                    if l.att == 'debit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '再贴现',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': self[l.field.name],
                            'credit': 0.0
                        })
                    if l.att == 'credit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '再贴现',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': 0.0,
                            'credit': self[l.field.name]
                        })
                if l.value == 'code':
                    localdict = {}
                    for f in l.field_ids:
                        localdict[f.name] = self[f.name]
                    safe_eval(l.code, localdict, mode="exec", nocopy=True)
                    if l.att == 'debit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '再贴现',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': localdict['result'],
                            'credit': 0.0
                        })
                    if l.att == 'credit':
                        move.line_ids.sudo().create({
                            'move_id': move.id,
                            'name': '再贴现',
                            'partner_id': self.partner.id,
                            'account_id': l.account_id.id,
                            'date_maturity': self.buy_date,
                            'debit': 0.0,
                            'credit': localdict['result']
                        })

    @api.one
    def action_hold(self):
        self.state = 'hold'

    @api.one
    def action_pay(self):
        self.state = 'pay'

    @api.one
    def action_cancel(self):
        self.state = 'error'

    @api.one
    def action_buy(self):
        self.state = 'buy'
        self.atype = True


    @api.multi
    def my_other_logic(self, vals):
        my_trigger_field_value = vals.get('my_trigger_field_name')
        if my_trigger_field_value == 1:
            self.write({'another_field': 2})

    # @api.one
    # @api.onchange("hold_no")
    # def onchange_daily_financial(self):
    #     _logger.info("9999999999999999")
    #     _logger.info(self.hold_total_day)
    #     _logger.info(self.hold_total_profit)
    #     ticket = self.env['ticket.info'].search([('state','=','hold'),('ticket','=',self.id)])
    #     income = self.hold_total_income
    #     cost = self.hold_total_cost
    #     profit = self.hold_total_profit
    #     hold_total_day = self.hold_total_day
    #     if ticket:
    #         self.hold_total_day = len(ticket) + hold_total_day
    #         for t in ticket:
    #             income += t.income
    #             cost += t.cost
    #             profit += t.profit
    #         self.hold_total_cost = cost
    #         self.hold_total_income = income
    #         self.hold_total_profit = profit
        # else:
        #     # self.hold_total_day =
        #     if self.amount_date < fields.Date.today():
        #         if self.sell_date:
        #             day = (self.sell_date - self.buy_date).days
        #             self.hold_total_day = day
        #             self.hold_total_cost = self.daycost * day
        #             self.hold_total_income = self.everyday_income * day
        #             self.hold_total_profit = self.avedayprofit * day
        #         else:
        #             day = (self.amount_date - self.buy_date).days
        #             self.hold_total_day = day
        #             self.hold_total_cost = self.daycost * day
        #             self.hold_total_income = self.everyday_income * day
        #             self.hold_total_profit = self.avedayprofit * day
        #     else:
        #         if self.sell_date:
        #             day = (self.sell_date - self.buy_date).days
        #             self.hold_total_day = day
        #             self.hold_total_cost = self.daycost * day
        #             self.hold_total_income = self.everyday_income * day
        #             self.hold_total_profit = self.avedayprofit * day
        #         else:
        #             day = (fields.Date.today() - self.buy_date).days
        #             self.hold_total_day = day
        #             self.hold_total_cost = self.daycost * day
        #             self.hold_total_income = self.everyday_income * day
        #             self.hold_total_profit = self.avedayprofit * day


class accountmove(models.Model):
    _inherit = 'account.move'

    ticket = fields.Many2one("affixed.ticket", u'贴票')
