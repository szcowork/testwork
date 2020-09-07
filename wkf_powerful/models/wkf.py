# -*- coding: utf-8 -*-
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from lxml import etree
from lxml.etree import XML, tostring
from .xml_templdate import *

import logging

_logger = logging.getLogger(__name__)


class wkf_base(models.Model):
    _name = 'wkf.base'
    _description = '工作审批流'
    _def_wkf_state_name = 'x_wkf_state'
    _def_wkf_note_name = 'x_wkf_note'

    @api.one
    @api.depends('node_ids')
    def _compute_default_state(self):
        def _get_start_state(nodes):
            if not nodes: return None
            star_id = nodes[0].id
            for n in nodes:
                if n.is_start:
                    star_id =n.id
                    break
            return str(star_id)

        nodes = self.node_ids
        show_nodes = filter(lambda x: x.show_state, nodes)
        no_rest_nodes = filter(lambda x: x.no_reset, nodes)

        self.show_states = ','.join([str(x.id) for x in show_nodes])
        self.default_state = _get_start_state(nodes)
        self.no_reset_states =','.join(["'%s'" % x.id for x in no_rest_nodes])

    @api.model
    def _default_reset_group(self):
        return self.env['ir.model.data'].xmlid_to_res_id('base.group_system')

    name = fields.Char('名称', required=True,)
    model_id = fields.Many2one('ir.model', '模型', required=True, help="选择需要创建工作审批流的模型")
    model = fields.Char(related='model_id.model', string='模型名称', readonly=True)
    model_view_id = fields.Many2one('ir.ui.view', '工作审批流展示form视图', help="选择需要展示工作审批流的form(表单)视图")
    model_tree_view_ids = fields.Many2many('ir.ui.view', string='工作审批流展示tree视图', help="选择需要展示工作审批流的tree(列表)视图")
    view_id = fields.Many2one('ir.ui.view', '工作审批流视图(自动创建)', readonly=True, help="扩展工作审批流的视图ID, 确认后自动生成",)
    tree_view_ids = fields.Char(string='工作审批流tree视图(自动创建)',default='')
    node_ids = fields.One2many('wkf.node', 'wkf_id', '节点', help='Nodes')
    trans_ids = fields.One2many('wkf.trans', 'wkf_id', '流程', help='Transfers,')
    active = fields.Boolean('有效', default=True)
    field_id = fields.Many2one('ir.model.fields', 'Field Workflow-State', help="The Workflow State field", readonly=True)

    allow_reset = fields.Boolean("允许重置工作审批流", default=True, help="勾选时,可以被重置为草稿状态")
    reset_group = fields.Many2one('res.groups', "群组重置", default=_default_reset_group,  required=True, help="工作审批流重置权限群组, 默认为管理员" )
    no_reset_states = fields.Char(compute='_compute_default_state', string='不可重置', help='Which state u can to reset the Workflow')

    default_state = fields.Char(compute='_compute_default_state', string="默认工作审批流状态", store=False, help='The default Workflow state, It is come from the star node')
    show_states = fields.Char(compute='_compute_default_state', string="默认显示状态", store=False, help='Which status can show the state widget, It is set by node')

    @api.model
    def get_default_state(self, model):
        return self.search([('model','=',model)]).default_state

    def sync2ref_model(self):
        self.ensure_one()
        self._check()
        self.make_field()
        self.make_view()
        self.make_tree_view()

    def _check(self):
        if not any([n.is_start for n in self.node_ids]):
            raise Warning('Please check the nodes setting, not found a start node')


    def make_wkf_contain(self):
        wkf_contain = XML(wkf_contain_template)
        wkf_contain.append(self.make_btm_contain())
        wkf_contain.append(XML(wfk_field_state_template % (self.field_id.name, self.show_states)))
        return wkf_contain

    def make_btm_contain(self):
        btn_contain = XML(bton_contain_template)
        for t in self.trans_ids:
            btn = XML(btn_template % {'btn_str': t.name, 'trans_id': t.id, 'vis_state': t.node_from.id})
            if t.group_ids:
                btn.set('groups', t.xml_groups)
            btn_contain.append(btn)

        btn_contain.append(XML(btn_show_log_template % {'btn_str': '审批日志', 'btn_grp': 'base.group_user'} ))
        btn_contain.append(XML(btn_wkf_reset_template % {'btn_str': '重置审批流', 'btn_grp': 'base.group_system', 'btn_ctx': self.id, 'no_reset_states': self.no_reset_states }  ))
        return btn_contain

    def make_view(self):
        self.ensure_one()
        view_obj = self.env['ir.ui.view']
        have_header = '<header>' in self.model_view_id.arch
        arch = have_header and  XML(arch_template_header) or XML(arch_template_no_header)
        #wkf_contain = XML("""<div style="background-color:#7B68EE;border-radius:2px;display: inline-block;padding-right: 4px;"></div>""")

        wkf_contain = self.make_wkf_contain()

        arch.insert(0, wkf_contain)

        view_data = {
            'name':  '%s.WKF.form.view' % self.model,
            'type': 'form',
            'model': self.model,
            'inherit_id': self.model_view_id.id,
            'mode': 'extension',
            'arch': tostring(arch),
            'priority': 99999,
        }

        #update or create view
        view = self.view_id
        if not view:
            view = view_obj.create(view_data)
            self.write({'view_id': view.id})
        else:
            view.write(view_data)

        return True

    def make_tree_view(self):
        self.ensure_one()
        view_obj = self.env['ir.ui.view']
        for tree_id in self.model_tree_view_ids:
            view_data = {
                'name':  '%s.WKF.tree.view' % self.model,
                'type': 'tree',
                'model': self.model,
                'inherit_id': tree_id.id,
                'mode': 'extension',
                'arch': '<xpath expr="//field[last()]" position="after"> <field name="x_wkf_state"/></xpath>',
                'priority': 99999,
            }

            #update or create view
            # view = self.view_id
            view = None
            for view in tree_id.inherit_children_ids:
                if( 'WKF.tree.view' in view.name ):
                    return view
            if view:
                view.write(view_data)
            else:
                view_id = view_obj.create(view_data)
                if self.tree_view_ids:
                   self.tree_view_ids = self.tree_view_ids + ','+str(view_id.id)
                else:
                    self.tree_view_ids = str(view_id.id)
                # self.tree_view_ids = [(0, 0,[view_id])]

        return True

    def make_tree_view_unlink(self):
        self.ensure_one()
        if self.tree_view_ids:
            _logger.info(self.tree_view_ids)
            tmp_view_ids = self.tree_view_ids.split(',')
            view_ids = []
            for view_id in tmp_view_ids:
                view_ids.append(int(view_id))
            _logger.info(view_ids)
            self.env['ir.ui.view'].browse(view_ids).unlink()
            self.tree_view_ids = ''


    def make_field(self):
        self.ensure_one()
        fd_obj = self.env['ir.model.fields']
        fd_id = fd_obj.search([('name','=',self._def_wkf_state_name),('model_id','=', self.model_id.id) ])
        fd_id2 = fd_obj.search([('name','=',self._def_wkf_note_name),('model_id','=', self.model_id.id) ])
        fd_data = {
            'name': self._def_wkf_state_name,
            'ttype': 'selection',
            'state': 'manual',
            'model_id': self.model_id.id,
            'model': self.model_id.model,
            'modules': self.model_id.modules,
            'field_description': u'审批状态',
            #'select_level': '1',
            'selection': str(self.get_state_selection()),
        }
        if fd_id:
            fd_id.write(fd_data)
        else:
            fd_id = fd_obj.create(fd_data)

        self.write({'field_id': fd_id.id})
        return True

    @api.model
    def get_state_selection(self):
        return [(str(i.id), i.name) for i in self.node_ids]

    def action_no_active(self):
        self.ensure_one()
        self.make_tree_view_unlink()
        self.view_id.unlink()
        self.field_id.unlink()
        #self.active = False
        return True




class wkf_node(models.Model):
    _name = "wkf.node"
    _order = 'sequence'
    _description = '工作节点'

    name = fields.Char('名称', required=True, help='A node is basic unit of Workflow')
    sequence = fields.Integer('序号')
    code = fields.Char('Python代码', required=False)
    wkf_id = fields.Many2one('wkf.base', '工作审批流', required=True, select=True, ondelete='cascade')
    split_mode = fields.Selection([ ('or','或'), ('and','与')], '分支模式', size=3, required=False)
    join_mode = fields.Selection([('or', '或'), ('and', '与')], '审核模式', size=3, required=True, default='or',
                                 help='或:任一流程审批通过, 即可进入此节点.  与:需要所有流程都审批通过, 才能进入此节点')
    #'kind': fields.selection([('dummy', 'Dummy'), ('function', 'Function'), ('subflow', 'Subflow'), ('stopall', 'Stop All')], 'Kind', required=True),
    action = fields.Char('Python函数',size=64, help='当进入本节点后, 可以触发该模型下的函数或者是执行其他代码, 比如sale.order中的确认订单button_confirm')
    arg = fields.Text('函数参数',size=64, help='触发模型函数的参数')
    #'action_id': fields.many2one('ir.actions.server', 'Server Action', ondelete='set null'),
    is_start = fields.Boolean('起始节点', help='This node is the start of the Workflow')
    is_stop =fields.Boolean('结束节点',  help='This node is the end of the Workflow')
    #'subflow_id': fields.many2one('workflow', 'Subflow'),
    #'signal_send': fields.char('Signal (subflow.*)'),
    out_trans = fields.One2many('wkf.trans', 'node_from', '流出流程', help='The out transfer of this node')
    in_trans = fields.One2many('wkf.trans', 'node_to', '流入流程', help='The input transfer of this node')
    show_state = fields.Boolean('显示在工作审批流', default=True,  help="If True, This node will show in Workflow states")
    no_reset = fields.Boolean('不可重置', default=True,  help="If True, this Node not display the Reset button, default is True")
    event_need = fields.Boolean('创建日历事件', help="If true, When Workflow arrived this node, will create a calendar event relation users")
    event_users = fields.Many2many('res.users', 'event_users_trans_ref', 'tid', 'uid', '日历事件相关人员', help="The calendar event users")

    def backward_cancel_logs(self, res_id):
        """
        cancel the logs from this node, and create_date after the logs
        """
        log_obj = self.env['log.wkf.trans']
        logs = log_obj.search([('res_id','=',res_id),('trans_id.node_from.id','=',self.id)])
        if logs:
            min_date = min([x.create_date for x in logs])
            logs2 = log_obj.search([('res_id','=',res_id),('create_date','>=',min_date)])
            logs.write({'active': False})
            logs2.write({'active': False})


    def check_trans_in(self, res_id):
        self.ensure_one()

        flag = True
        join_mode = self.join_mode
        log_obj = self.env['log.wkf.trans']
        flag = False
        if join_mode == 'or':
            flag = True
        else:
            in_trans = filter(lambda x:x.is_backward is False, self.in_trans)
            trans_ids = [x.id for x in in_trans]
            logs = log_obj.search([('res_id','=', res_id),('trans_id','in', trans_ids)])
            log_trans_ids = [x.trans_id.id for x in logs]
            flag = set(trans_ids) == set(log_trans_ids) and True or False
        return flag


    def make_event(self, name):
        data = {
            'name': '%s %s' % (name, self.name),
            'state': 'open',  # to block that meeting date in the calendar
            'partner_ids': [(6, 0, [u.partner_id.id for u in self.event_users])],
            'start': fields.Datetime.now(),
            'stop': fields.Datetime.now(),
            'start_datetime': fields.Datetime.now(),
            'stop_datetime': fields.Datetime.now(),
            'duration': 1,
            'alarm_ids': [(6,0,[1])],
        }
        self.env['calendar.event'].create(data)
        return True


class wkf_trans(models.Model):
    _name = "wkf.trans"
    _order = "sequence"
    _description = '审批流程'

    @api.one
    @api.depends('group_ids')
    def _compute_xml_groups(self):
        data_obj = self.env['ir.model.data']
        xml_ids = []
        for g in self.group_ids:
            data = data_obj.search([('res_id','=',g.id),('model','=','res.groups')])
            xml_ids.append( data.complete_name )
        self.xml_groups = xml_ids and ','.join(xml_ids) or False


    name = fields.Char("名称", required=True, help='流程就是从一个节点到另一个节点')
    code = fields.Char('Python代码', required=False)
    group_ids = fields.Many2many('res.groups', 'group_trans_ref', 'tid', 'gid', '群组', help="有权限审批本流程的群组")
    condition = fields.Char('条件', required=True, default='True', help='审批条件，默认为True')
    node_from = fields.Many2one('wkf.node', '发起节点', required=True, select=True, ondelete='cascade',)
    node_to = fields.Many2one('wkf.node', '目标节点', required=True, select=True, ondelete='cascade')
    wkf_id = fields.Many2one('wkf.base', related='node_from.wkf_id', store=True)
    model = fields.Char(related='wkf_id.model')
    xml_groups = fields.Char(compute='_compute_xml_groups', string='XML视图群组')
    is_backward = fields.Boolean(u'可反审核', help="Is a Reverse transfer")
    auto = fields.Boolean(u'自动审批', help="为真时, 当条件满足了, 自动完成审批。勾选后不创建审批按钮, 默认为False")
    sequence = fields.Integer('序号')
    need_note = fields.Boolean('强制备注', help="为真时，备注必填，通常用于可反审核流程")

    @api.one
    def make_log(self, res_name, res_id, note=''):
        return  self.env['log.wkf.trans'].create({'name':res_name, 'res_id': res_id, 'trans_id':self.id, 'note': note})

class log_wkf_trans(models.Model):
    _name = "log.wkf.trans"
    _description = '审批日志'

    name = fields.Char('名称')
    trans_id = fields.Many2one('wkf.trans', '流程')
    model = fields.Char(related='trans_id.model', string='Model')
    res_id = fields.Integer('Resource ID')
    active = fields.Boolean('有效', default=True)
    note = fields.Text('备注', help="用于备注该审批")
























