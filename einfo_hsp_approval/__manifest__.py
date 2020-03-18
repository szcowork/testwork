# -*- coding: utf-8 -*-
{
   'name': "einfo审批流插件",

   'summary': """
    根据HR的人事结构进行审批""",

   'description': """
    
   """,

   'author': "Einfo-Tech",
   'website': "http://www.einfo-tech.com",
   'category': 'Tools',
   'version': '1.0',

   'depends': ['base','hr','hr_org_chart'],

   'data': [
        "security/ir.model.access.csv",
		   "views/templates.xml", 
         "security/res.groups.xml", 
   ],
   'qweb': [
        'static/src/xml/hr_org_chart.xml',
    ],

   "installable":True,

}