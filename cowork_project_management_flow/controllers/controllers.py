# -*- coding: utf-8 -*-
import os, io
from odoo import http
from odoo.http import content_disposition, request
import werkzeug
import werkzeug.wrappers
import odoo.tools
import xlwt
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class CoworkProjectManagementFlow(http.Controller):
    @http.route('/cowork_quote/<rec_id>', type='http', auth="user")
    def code_output(self, name=None, rec_id=None, **kw):
        # try:
        tz = io.BytesIO()
        
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER
        style = xlwt.XFStyle()
        style.alignment = alignment
        
        borders = xlwt.Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1
        borders.bottom_colour = 0x3A
        style.borders = borders
        
        wb = xlwt.Workbook(encoding='utf-8')
        sheet = wb.add_sheet('询价单')
        row = ['供应商','图号/名称','名称/型号','数量','单位','材料','类型','品牌','含税单价','含税金额','货期(天)','备注']
        width = len(row)
        sheet.write_merge(0, 0, 0, width-1, '柯沃工业采购清单', style)

        for c in range(width):
            sheet.write(1,c,row[c])

        rec = request.env['cowork.purchase'].search([('id','=',rec_id)])
        pids = []
        for line in rec.line_id:
            pids.append(line.product_id.id)
        pids = list(set(pids))
        length = len(pids)

        for index in range(length):
            count = 0
            for line in rec.line_id:
                if line.product_id.id == pids[index]:
                    count += line.product_qty
                    categ_id = line.categ_id
                    product_id = line.product_id
                    uom_id = line.uom_id
                    material = line.material
                    type_id = line.type_id
                    brand_id = line.brand_id
                    # tax_ids = line.tax_ids
                    comment = line.comment
            vals = ['',categ_id.name,product_id.name,count,uom_id.name if uom_id else "",material if material else "",type_id.name if type_id else "",brand_id.name,0,0,0,comment if comment else ""]
            _logger.info(vals)
            for i in range(width):
                sheet.write(index+2,i,vals[i])
        
        wb.save(tz)
        headers = [('Content-Disposition',content_disposition("询价单.xls")),
                    ('Content-Type', "application/vnd.ms-excel")]
        response = werkzeug.wrappers.Response(tz.getvalue(), headers=headers, direct_passthrough=True)
        return response

        # except Exception as e:
        #     error = "输出遭遇错误: %s" % (str(e) or repr(e))
        #     raise UserError(error)
