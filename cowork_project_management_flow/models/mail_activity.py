# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class mail_activity(models.Model):
    _inherit = "mail.activity"

    @api.model
    def _cron_create_activity_message(self):
        today = fields.Date.today()
        activity = self.env['mail.activity'].search([('date_deadline','=',today)])
        if activity:
            for act in activity:
                qywx = self.env['einfo.qywx.application']
                if act.res_model_id:
                    recs = qywx.search([("model_ids","in",act.res_model_id.id)])
                    if recs:
                        record_field = self.env['ir.model.fields'].search([('name','=','user_id'),('model_id','=',act.res_model_id.id)])
                        user = False
                        if record_field:
                            r = self.env[act.res_model].sudo().search([('id','=',act.res_id)])
                            if r and r.user_id:
                                user = r.user_id.name

                        message = {}
                        message['model'] = act.res_model
                        message['res_id'] = act.res_id
                        message['author_id'] = act.user_id.id
                        message['body'] = act.note
                        for rec in recs:
                            rec.sudo().send_mail_message(message,user)