# -*- coding: utf-8 -*-
{
    'name': "柯沃项目式销售",

    'summary': """
     柯沃项目式销售""",

    'description': """
     待补充
    """,

    'author': "Einfo-Tech",
    'website': "http://www.einfo-tech.com",
    'category': 'Tools',
    'version': '1.0',

    'depends': ['base','mail','sale','purchase'],

    'data': [
        "views/cowork_project_availability_analysis.xml",
        "views/cowork_technical_analysis.xml",
        "views/cowork_project_difficulty.xml",
        "views/cowork_project_priority.xml",
        "security/groups_config.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "data/cowork_project_difficulty.xml",
        "data/cowork_project_priority.xml",
        "views/order.xml"
    ],

    'installable':True,
    'application':True,

}