# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _ ,exceptions
import time
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


    
class import_bom_line_wizard(models.TransientModel):
    _name = 'import.bom.line.wizard'
    _description ='导入BOM清单'

    bom_file = fields.Binary(string="选择文件")
    import_option = fields.Selection([('xls', 'XLS'),('csv', 'CSV')],string='选择格式',default='xls')
    user_id = fields.Many2one(comodel_name="res.users", default=lambda self: self.env.user, string="编制")

    @api.multi
    def import_bom(self):
        if self.import_option == 'csv':
            # keys = ['class_id','class_categ_id','categ_id','product_tmpl_id','brand_id','count','uom_id','material','comments']
            keys = ['class_categ_id','categ_id','product_tmpl_id','count','uom_id','material','class_id','brand_id','comments','code']
            csv_data = base64.b64decode(self.bom_file)
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
                        res = self.create_bom_line(values, i+1)
        else:
            fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
            try:
                fp.write(binascii.a2b_base64(self.bom_file))
            except Exception:
                raise exceptions.Warning("该文件无效或没有上传文件")
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet_no = workbook.nsheets
            # sheet = workbook.sheet_by_index(0)
            for i in range(sheet_no):
                sheet = workbook.sheet_by_index(i)
                sheetname = sheet.name
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 4:      #0:
                        fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or ustr(row.value), sheet.row(row_no)))
                        # keys = ['class_categ_id','categ_id','product_tmpl_id','count','uom_id','material','class_id','brand_id','comments']
                        _logger.info("?????????????/")
                        _logger.info(line[10])
                        t1 = False
                        if line[10]:
                            t1 = xlrd.xldate.xldate_as_datetime(float(line[10]), 0)
                            t1 = t1.strftime('%Y-%m-%d')
                        code = False
                        if line[2]:  #判断是否含有条码
                            code = line[2].split('.')[0]
                        values.update({
                                'class_categ_id' : sheetname,#line[0],
                                'categ_id' : line[3],
                                'product_tmpl_id' : line[4].split('.')[0],
                                'count' : line[5],
                                'uom_id' : line[7],
                                'material' : line[9],
                                'buy_no': line[6],
                                'class_id' : line[1],
                                'brand_id' : line[8],
                                'comments' : line[11],
                                'date': t1,
                                'code': code
                        })
                        res = self.create_bom_line(values, row_no+1)
        return res

    @api.multi
    def create_bom_line(self,values,row_no):
        bom_id=self.env['cowork.bom'].browse(self._context.get('active_id'))
        class_categ_tmp = False
        class_categ_id = self.env['cowork.material.category'].search([('name','=',values['class_categ_id'])])
        if class_categ_id:
            class_categ_tmp = class_categ_id[0].id
        else: raise UserError("第%d行 部门\"%s\"不存在"%(row_no, values['class_categ_id']))

        class_tmp = False
        class_id = self.env['cowork.material.class'].search([('name','=',values['class_id']),('categ_id','=',class_categ_tmp)])#分类
        if class_id:
            class_tmp = class_id[0].id
        else: raise UserError("第%d行 类型\"%s\"不存在"%(row_no, values['class_id']))

        categ_tmp = False
        categ_id = self.env['product.category'].search([('name','=',values['categ_id'])])
        if categ_id:
            categ_tmp = categ_id[0].id
        else: #raise UserError("第%d行 产品\"%s\"不存在"%(row_no, values['categ_id']))
            categ_tmp = self.env['product.category'].create({
                'name': values['categ_id'],
                'property_cost_method': 'standard'
            })
            categ_tmp = categ_tmp.id

        brand_tmp = False
        brand_id = self.env['product.brand'].search([('name','=',values['brand_id'])])
        if brand_id:
            brand_tmp = brand_id[0].id
        else:
            brand_tmp = self.env['product.brand'].create({'name':values['brand_id']}).id
        # else: raise UserError("第%d行 品牌\"%s\"不存在"%(row_no, values['brand_id']))
        
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
        product_obj_search=self.env['product.template'].search([('name', '=',values['product_tmpl_id']),('barcode','=',values['code'])])
        product_id = False
        if product_obj_search:
            product_id=product_obj_search[0].id
        else: #raise UserError("第%d行 规格\"%s\"不存在"%(row_no, values['product_tmpl_id']))
            _logger.info(uom_tmp)
            _logger.info(categ_tmp)
            product_id = self.env['product.template'].create({
                'name':values['product_tmpl_id'],
                'type': 'product',
                'categ_id': categ_tmp,
                'uom_id': uom_tmp,
                'uom_po_id': uom_tmp,
                'barcode': values['code']
            })
            product_id = product_id.id

        bom_lines=self.env['cowork.bom.material.part'].create({
                                            'bom_id':bom_id.id,
                                            'product_tmpl_id': product_id,
                                            'count':values.get('count'),
                                            'comments':values.get('comments'),
                                            'class_id': class_tmp,
                                            'class_categ_id': class_categ_tmp,
                                            'categ_id': categ_tmp,
                                            'brand_id': brand_tmp,
                                            'uom_id': uom_tmp,
                                            'material': values.get('material'),
                                            'purchase_buy': values.get('buy_no'),
                                            'plan_date': values.get('date')
                                            })

        bom_id.user_id = self.user_id.id
        return True
    
class import_purchase_line_wizard(models.TransientModel):
    _name = 'import.purchase.line.wizard'
    _description ='更新询价明细'

    purchase_file = fields.Binary(string="选择文件")
    import_option = fields.Selection([('xls', 'XLS'),('csv', 'CSV')],string='选择格式',default='xls')

    @api.multi
    def import_bom(self):
        if self.import_option == 'csv':
            keys = ['price','tax','price_tax','days','comments','product','partner']
            csv_data = base64.b64decode(self.purchase_file)
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
                        res = self.update_purchase_line(values, i+1)
        else:
            fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
            try:
                fp.write(binascii.a2b_base64(self.purchase_file))
            except Exception:
                raise exceptions.Warning("该文件无效或没有上传文件")
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet_no = workbook.nsheets
            for i in range(sheet_no):
                sheet = workbook.sheet_by_index(i)
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 1:
                        fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                    else:
                        line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or ustr(row.value), sheet.row(row_no)))                  
                        values.update({
                                'price' : line[8],
                                'tax' : line[9],
                                'price_tax' : line[10],
                                'days' : line[11].split('.')[0],
                                'comments' : line[12],
                                'product': line[2],
                                'partner': line[0].split('.')[0]
                        })
                        res = self.update_purchase_line(values, row_no+1)
        return res

    @api.multi
    def update_purchase_line(self,values,row_no):
        purchase_id=self.env['cowork.purchase'].browse(self._context.get('active_id'))
        if purchase_id.pline_id:
            partner_id = self.env['res.partner'].search([('name','=',values['partner'])])
            if partner_id:
                partner_id = partner_id[0]
            else:
                partner_id = self.env['res.partner'].create({
                    'name': values['partner'],
                    'customer': False,
                    'supplier': True
                })
            for line in purchase_id.pline_id:
                product_search=self.env['product.product'].search([('name', '=',values['product'])])
                if product_search:
                    if line.product_id.id == product_search[0].id:
                        val_tax = values['tax']
                        _logger.info(val_tax)
                        if val_tax:
                            val_tax = str(float(val_tax)*100)
                            val_tax = val_tax.split('.')[0] + '%'
                            _logger.info(val_tax)
                            tax = self.env['account.tax'].search([('type_tax_use','=','purchase'),('name','=',val_tax)])
                            if tax:
                                tax = [(6, 0, [tax.id])]
                            else:
                                tax = False
                        else:
                            tax = False
                        _logger.info("888888888888888")  
                        _logger.info(tax)
                        line.write({
                            'partner_id': partner_id.id,
                            'list_price': values.get('price'),
                            'delivery': values.get('days'),
                            'tax_ids': tax
                        })
                else:
                    raise UserError("无法查询产品\"%s\"!"%values['product'])

        return True