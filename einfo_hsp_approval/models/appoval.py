# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
class msg(models.Model):
    _name = "approval.msg"

    employee_id = fields.Many2one(comodel_name="hr.employee",string='审批人')
    state = fields.Selection(selection=[('PASS','同意'),('UNPASS','不同意')])
    time = fields.Datetime(string='审批时间')
    # sequence = fields.Integer(string='序号')

class approval_node(models.Model):
    _name = "einfo.approval.node"
    _description = "审批节点"

    job = fields.Many2one('hr.job', string='岗位',)
    department_id = fields.Many2one('hr.department', string='部门',)
    is_node = fields.Boolean('可审批通过')
    model_name = fields.Char(string='模型')
    # einfo_approval_id = fields.Many2one('einfo.approval',string='审批')


class approval(models.Model):
    _name = "einfo.approval"
    _description = "审批"

    @api.model
    def default_get(self, fields):
        res = super(approval, self).default_get(fields)
        # _logger.info(self.env.user.employee_ids)
        # _logger.info(self.env.user.employee_ids[0].id)
        if len(self.env.user.employee_ids) > 0:
            res.update({
            'start_approval_employee_id': self.env.user.employee_ids[0].id,
            })
        return res

    approval_msg_ids = fields.Many2many(comodel_name="approval.msg",string='审批信息')
    approval_state = fields.Selection(selection=[('draft','草稿'),('approvaling','审批中'),('pass','通过'),('unpass','不通过')],default='draft',string="审批状态")
    start_approval_employee_id = fields.Many2one(comodel_name="hr.employee",required=True,string='审批发起者',)
    start_approval_time = fields.Datetime(string='开始审批时间')
    tem_approval_field = fields.Char(default='..')
    # eply = fields.Many2one(comodel_name="hr.employee", related="start_approval_employee_id", string="员工",)
    job_id = fields.Many2one('hr.job',related="start_approval_employee_id.job_id",string="岗位")
    current_approval_employee_id = fields.Many2one(comodel_name="hr.employee",string='当前审批人',compute='_compute_approval_employee')
    # approval_node_ids = fields.Many2many('einfo.approval.node',string='审批节点')

    # def _default_employee(self):
    #     _logger.info(self.env.user.partner_id.)
    #     pass

    @api.depends('approval_msg_ids')
    def _compute_approval_employee(self):
        for record in self:
            #如果通过或者不通过，则当前审批人为空
            if record.approval_state == 'pass' or record.approval_state == 'unpass':
                record.current_approval_employee_id = False
                return
            # compute employee data for org chart
            ancestors, current = self.env['hr.employee'], record.start_approval_employee_id
            while current.parent_id:
                ancestors += current.parent_id
                current = current.parent_id
            
            #如果审批信息列表为空，则当前审批人为审批发起者
            if len(record.approval_msg_ids) == 0 :
                record.current_approval_employee_id = record.start_approval_employee_id.id
            else:
                parent_ids = record.approval_msg_ids.mapped('employee_id').mapped('id')
                #按顺序遍历审批发起者的上级，当遍历的上级发现不在审批信息列表里面，说明该上级还没有处理，
                #把该上级设置成当前审批者
                for tem_employee in ancestors:
                    if tem_employee.id not in parent_ids:
                        record.current_approval_employee_id = tem_employee.id
                        break
            

