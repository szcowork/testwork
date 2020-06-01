# -*- coding: utf-8 -*-
{
   'name': "柯沃日常管理",

   'summary': """
    日常管理""",

   'description': """
    
   """,

   'author': "Einfo-Tech",
   'website': "http://www.einfo-tech.com",
   'category': 'Tools',
   'version': '1.0',

   'depends': ['base','einfo_hsp_approval','einfo_code_manager'],  #,'cowork_projecty_sales'

   'data': [
      
 		# "security/res.groups.xml",
      "security/ir.model.access.csv",
		"views/overtime_appoval.xml", 
		"views/duty_type.xml", 
		"views/duty_approval.xml", 
		"views/hire_approval.xml", 
		"views/hire_check.xml", 
		"views/overtime_type.xml", 
		"views/business_travel_appoval.xml", 
		"views/reimbursement_appoval.xml", 
		"views/reimbursement_account.xml", 
      "views/product_appoval.xml",
 		"views/menu.xml",
      "views/rule.xml",
      "views/template.xml",
      "views/bom_approval.xml"
   ],

   "installable":True,

}