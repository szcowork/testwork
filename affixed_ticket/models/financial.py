# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class daily_financial(models.Model):
    _name = "daily.financial"
    _description = u'每日财务记录'

    currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
        default=lambda self: self.env.user.company_id.currency_id.id)
        
    date = fields.Date(u'日期')
    name = fields.Char(u'单号', default='New',readonly=True)
    yes_crash = fields.Monetary(u'昨日现金余额')
    to_crash = fields.Monetary(u'今日现金余额')
    crash = fields.Monetary(u'现金发生额')
    yes_ticket = fields.Monetary(u'昨日票据余额')
    to_ticket = fields.Monetary(u'今日票据余额')
    ticket = fields.Monetary(u'票据发生额')
    profit = fields.Monetary(u'当日实际利润')

    hold_no = fields.Integer(u'持票数',compute='_compute_hold_ids')
    # hold = fields.One2many('ticket.info','hold',u'持票中')
    # hold = fields.One2many('affixed.ticket','hold',u'持票中') #ondelete='cascade'
    hold_cost = fields.Monetary(u'今日持有票据占用资金总和')
    hold_mine = fields.Monetary(u'今日持有票据自有资金成本之和')
    hold_profit = fields.Monetary(u'持票合计利润')

    rediscount_no = fields.Integer(u'再贴现和到期兑付总数',compute='_compute_rediscount_ids')
    # rediscount = fields.One2many('ticket.info','rediscount',u'再贴现与到期兑付')
    # rediscount = fields.One2many('affixed.ticket','rediscount',u'再贴现与到期兑付')
    rediscount_get = fields.Monetary(u'今日再贴现和持有到期对付收到现金之和')
    rediscount_profit = fields.Monetary(u'再贴现与到期兑付合计利润')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq = self.env['ir.sequence'].next_by_code('daily.financial') or '/'
            vals['name'] = seq
        return super(daily_financial, self).create(vals)

    # @api.model   #自动化动作函数
    @api.multi
    def just_atest(self):
        date = fields.Date.today()
        detaday=timedelta(days=1)
        date = date - detaday
        financial = self.env['daily.financial'].search([])
        if len(financial) < 1:
            config = self.env["ir.config_parameter"]
            first_crash = float(config.get_param('affixed_ticket.first_crash'))
            first_ticket = float(config.get_param('affixed_ticket.first_ticket'))
        else:
            first_crash = financial[-1].to_crash
            first_ticket = financial[-1].to_ticket

        # date = fields.Date.today()
        #计算现金发生额   票据发生额
        buy = 0
        sell = 0
        profit = 0
        buy_ticker = 0
        sell_ticker = 0
        profit_ticket = 0
        affixed = self.env['affixed.ticket'].search([])
        if affixed:
            for a in affixed:
                if a.buy_date == date:
                    buy += a.buycost
                    buy_ticker += a.amount

                if a.sell_date == date:
                    sell += a.sell_money
                    sell_ticker += a.amount

                if a.amount_date == date:
                    profit += a.amount
                    profit_ticket += a.amount
        
        crash = profit + sell - buy
        ticket = buy_ticker - sell_ticker - profit_ticket
        #每日报表
        daily = self.env['daily.financial'].create({
            'date':date,
            'yes_crash':first_crash,
            'to_crash':first_crash + crash,
            'crash':crash,
            'ticket':ticket,
            'yes_ticket':first_ticket,
            'to_ticket':ticket + first_ticket
        })

        hold = self.env['affixed.ticket'].search([('state','in',('hold','pay','buy')),('buy_date','<=',date)])  #贴现日小于等于昨天
        zijin = 0
        ziyou_zijin = 0
        hold_profit = 0
        for h in hold:
            if h.sell_date and h.sell_date > date:
                zijin += h.buycost
                ziyou_zijin += h.daycost
                hold_profit += h.avedayprofit
                self.env['ticket.info'].create({
                    'name':date,
                    'hold':daily.id,
                    'ticket':h.id,
                    'income':h.everyday_income, #h.planprofit/h.plandays*1.0,
                    'cost':h.daycost,
                    'profit':h.avedayprofit,
                    'state':'hold'
                })
            if h.sell_date == False and h.amount_date > date:
                _logger.info(h)
                zijin += h.buycost
                ziyou_zijin += h.daycost
                hold_profit += h.avedayprofit
                self.env['ticket.info'].create({
                    'name':date,
                    'hold':daily.id,
                    'ticket':h.id,
                    'income':h.everyday_income,   #h.planprofit/h.plandays*1.0,
                    'cost':h.daycost,
                    'profit':h.avedayprofit,
                    'state':'hold'
                })
                _logger.info("3333333333333")
                affixed_ticket = self.env['ticket.info'].search([('state','=','hold'),('ticket','=',h.id)])
                # _logger.info(h.hold_total_day)   
                day = h.hold_total_day + len(affixed_ticket)
                daycost = h.daycost
                everyday_income = h.everyday_income
                avedayprofit = h.avedayprofit
                _logger.info(avedayprofit)
                # self.env['affixed.ticket'].search([('id','=',h.id)]).sudo().write({
                #     'hold_total_profit':avedayprofit*day,
                #     'hold_total_income':everyday_income*day,
                #     'hold_total_cost':daycost*day,
                #     'hold_total_day':day
                # })
                h.hold_total_day = day
                h.hold_total_cost = daycost * day
                h.hold_total_income = everyday_income * day
                h.hold_total_profit = avedayprofit * day
                # _logger.info("1010101010101010")
        # for h in hold:
        #     zijin += h.buycost
        #     ziyou_zijin += h.daycost
        #     hold_profit += h.avedayprofit
        #     self.env['ticket.info'].create({
        #         'name':fields.Date.today(),
        #         'hold':daily.id,
        #         'ticket':h.id,
        #         'profit':h.avedayprofit,
        #         'state':u'持票中'
        #     })
        sel = self.env['affixed.ticket'].search([('state','in',('buy','pay'))])  #再贴现与兑付
        xianjin = 0
        rediscount_profit = 0
        for s in sel:
            if s.sell_date == date:  #再贴现
                xianjin += s.sell_money_true
                rediscount_profit += s.sell_profit
                self.env['ticket.info'].create({
                    'name':date,
                    'rediscount':daily.id,
                    'ticket':s.id,
                    'state':'buy',
                    'income':s.sell_total,
                    'cost':s.sell_cost,
                    'profit':s.sell_profit   #再贴现利润????????
                })
            if s.amount_date == date and s.sell_date == None:  #到期兑付且没有发生再贴现的
                xianjin += s.amount
                # rediscount_profit += s.avedayprofit
                self.env['ticket.info'].create({
                    'name':date,
                    'rediscount':daily.id,
                    'ticket':s.id,
                    'income':0,
                    'cost':0,
                    'state':'pay',
                    'profit':0   #s.avedayprofit   #实际利润?????
                })

        daily.write({
            'hold_cost':zijin,
            'hold_mine':ziyou_zijin,
            'hold_profit':hold_profit,
            'rediscount_get':xianjin,
            'rediscount_profit':rediscount_profit,
            'profit':hold_profit + rediscount_profit
        })


    @api.multi
    def _compute_hold_ids(self):
        for order in self:
            hold = self.env['ticket.info'].search([('hold', '=', self.id)])
            order.hold_no = len(hold)

    @api.multi
    def _compute_rediscount_ids(self):
        for order in self:
            rediscount = self.env['ticket.info'].search([('rediscount', '=', self.id)])
            order.rediscount_no = len(rediscount)

    @api.multi
    def action_view_hold(self):
        action = {
            'name': u'持票中',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ticket.info',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('hold', '=', self.id)],  
        }
        return action

    @api.multi
    def action_view_rediscount(self):
        action = {
            'name': u'再贴现和到期兑付',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ticket.info',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('rediscount', '=', self.id)],  
        }
        return action

class ticket_info(models.Model):
    _name = "ticket.info"
    _description = u'每日票据信息'

    name = fields.Date('日期')
    ticket = fields.Many2one("affixed.ticket",u'票据')
    hold = fields.Many2one('daily.financial')
    rediscount = fields.Many2one('daily.financial')
    income = fields.Monetary(u'今日收入')
    cost = fields.Monetary(u'今日成本')
    profit = fields.Monetary(u'今日利润')
    state = fields.Selection([
        ('hold',u'持票中'),
        ('pay',u'兑付'),
        ('buy',u'再贴现')
    ],u'状态')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
        default=lambda self: self.env.user.company_id.currency_id.id)

class TicketWizard(models.TransientModel):
    _name = "ticket.wizard"
    _description = u'账户变化查询'

    start_month = fields.Date('开始日期', required=True)
    end_month = fields.Date('截止日期', required=True)

    @api.multi
    def print_search(self):
        self.ensure_one()
        start = self.start_month
        end = self.end_month
        cost = 0   #购票成本
        buy = 0   #再贴现利润
        hold = 0
        financial = self.env['daily.financial'].search([('date','>=',start),('date','<=',end)])
        for f in financial:
            hold += f.hold_profit
            buy += f.rediscount_profit
            cost += f.hold_cost

        ticket = self.env['profit.wizard'].create({
            'name':str(start) + "-" + str(end),
            'start_month':start,
            'end_month':end,
            'hold_cost':cost,
            'hold_profit':hold,
            'rediscount_profit':buy,
            'profit':hold + buy
        })
        action = {
            'name': u'账户查询',
            'view_mode': 'form',
            'res_model': 'profit.wizard',
            'view_id': self.env.ref('affixed_ticket.daily_financial_form_2').id,
            'type': 'ir.actions.act_window',
            'res_id':ticket.id
        }
        return action

class ProfitWizard(models.TransientModel):
    _name = "profit.wizard"
    _description = u'账户变化查询结果'

    name = fields.Char(u'查询记录')
    start_month = fields.Date('开始日期', required=True)
    end_month = fields.Date('截止日期', required=True)
    profit = fields.Monetary(u'总利润')
    rediscount_profit = fields.Monetary(u'再贴现与到期兑付合计利润')
    hold_profit = fields.Monetary(u'持票合计利润')
    hold_cost = fields.Monetary(u'今日持有票据占用资金总和')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, \
        default=lambda self: self.env.user.company_id.currency_id.id)