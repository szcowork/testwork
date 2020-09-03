# -*- coding: utf-8 -*-
import os, io
from odoo import http
from odoo.http import content_disposition, request
import werkzeug
import werkzeug.wrappers
import odoo.tools
import xlsxwriter
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class CoworkProjectManagementFlow(http.Controller):
    @http.route('/cowork_quote/<rec_id>', type='http', auth="user")
    def xlsx_output(self, name=None, rec_id=None, **kw):
        # try:
        tz = io.BytesIO()
        wb = xlsxwriter.Workbook(tz)
        req_style = wb.add_format({'bold': True, 'font_size':24,'align':'center','valign':'vcenter'})
        sheet = wb.add_worksheet('柯沃工业采购清单')
        row = ['供应商','图号/名称','名称/型号','数量','单位','材料','类型','品牌','含税单价','税率','含税金额','货期(天)','备注']
        width = len(row)
        sheet.merge_range(0, 0, 0, width-1, '柯沃工业采购清单', req_style)

        for c in range(width):
            sheet.write(1,c,row[c])

        rec = request.env['cowork.purchase'].search([('id','=',rec_id)])

        index = 0
        for line in rec.pline_id:
            tax = ""
            for t in line.tax_ids:
                tax += t.name+' '
            vals = [
                '',
                line.categ_id.name,
                line.product_id.name,
                line.product_qty,
                line.uom_id.name if line.uom_id else "",
                line.material if line.material else "",
                line.type_id.name if line.type_id else "",
                line.brand_id.name if line.brand_id else "",
                0,
                tax,
                0,
                0,
                line.comment if line.comment else ""
            ]
            _logger.info(index)
            _logger.info(vals)
            for i in range(width):
                sheet.write(index+2,i,vals[i])
            index = index + 1
        
        wb.close()
        headers = [('Content-Disposition',content_disposition("询价单.xlsx")),
                    ('Content-Type', "application/vnd.ms-excel")]
        response = werkzeug.wrappers.Response(tz.getvalue(), headers=headers, direct_passthrough=True)
        return response

        # except Exception as e:
        #     error = "输出遭遇错误: %s" % (str(e) or repr(e))
        #     raise UserError(error)
