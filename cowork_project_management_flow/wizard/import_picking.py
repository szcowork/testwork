# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ ,exceptions
from datetime import datetime
from odoo.exceptions import Warning
import binascii
import tempfile
from tempfile import TemporaryFile
from odoo.exceptions import UserError, ValidationError
import logging
from odoo.tools import ustr
_logger = logging.getLogger(__name__)
import io

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
    
class import_picking_line_wizard(models.TransientModel):
    _name = 'import.picking.line.wizard'
    _description ='导入调拨清单'

    picking_file = fields.Binary(string="选择文件")
    import_option = fields.Selection([('xls', 'XLS'),('csv', 'CSV')],string='选择格式',default='xls')

    @api.multi
    def import_picking(self):
        if self.import_option == 'csv':
            keys = ['product_id','want_count','uom_id']
            csv_data = base64.b64decode(self.picking_file)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            try:
                file_reader.extend(csv_reader)
            except Exception:
                raise exceptions.Warning("该文件无效或没有上传文件")
            values = {}
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        res = self.create_move_line(values, i+1)
        else:
            fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
            try:
                fp.write(binascii.a2b_base64(self.picking_file))
            except Exception:
                raise exceptions.Warning("该文件无效或没有上传文件")
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet_no = workbook.nsheets
            # sheet = workbook.sheet_by_index(0)
            for i in range(sheet_no):
                sheet = workbook.sheet_by_index(i)
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or ustr(row.value), sheet.row(row_no)))
                        values.update({
                                'product_id' : line[0].split('.')[0],
                                'want_count' : line[1],
                                'uom_id' : line[2]
                        })
                        res = self.create_move_line(values, row_no+1)
        return res

    @api.multi
    def create_move_line(self,values,row_no):
        picking_id=self.env['stock.picking'].browse(self._context.get('active_id'))
        uom_tmp = False
        uom_id = self.env['uom.uom'].search([('name','=',values['uom_id'])])
        if uom_id:
            uom_tmp = uom_id[0].id
        else: #raise UserError("第%d行 单位\"%s\"不存在"%(row_no, values['uom_id']))
            uom_tmp = self.env['uom.uom'].create({
                'name': values['uom_id'],
                'category_id': 1,
                'uom_type': 'bigger',
                'rounding': 1.0
            })
            uom_tmp = uom_tmp.id
        product_obj_search=self.env['product.product'].search([('name', '=',values['product_id'])])
        product_id = False
        if product_obj_search:
            product_id=product_obj_search[0]
        else: 
            raise UserError("第%d行 规格\"%s\"不存在"%(row_no, values['product_id']))

        bom_lines=self.env['stock.move'].create({
                                            'picking_id':picking_id.id,
                                            'product_id': product_id.id,
                                            'product_uom_qty':values.get('want_count'),
                                            'product_uom': uom_tmp,
                                            'name': product_id.name,
                                            'location_id': picking_id.location_id.id,
                                            'location_dest_id': picking_id.location_dest_id.id,
                                            })
        return True