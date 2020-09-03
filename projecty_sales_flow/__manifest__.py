# -*- coding: utf-8 -*-
{
   'name': "项目式销售流程",

   'summary': """
    项目式销售流程""",

   'description': """
    待补充
   """,

   'author': "Einfo-Tech",
   'website': "http://www.einfo-tech.com",
   'category': 'Tools',
   'version': '1.0',

   'depends': ['base','sale_management','purchase','uom','purchase_requisition'],

   'data': [
		"views/sale_apply.xml", 
		"views/technical_confirmation.xml", 
		"security/ir.module.category.xml",
 		"security/res.groups.xml",
 		"security/ir.model.access.csv",
 		"security/ir.rule.xml",
 		"views/menu.xml",
      "views/inherit.xml",
      "views/template.xml",
   ],

   "installable":True,

}