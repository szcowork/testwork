# -*- coding: utf-8 -*-
{
    'name': "票据业务",

    'summary': """
        主要对公司贴票业务的管理""",

    'description': """
        
    """,

    'author': "易捷讯（深圳）科技有限公司",
    'website': "http://www.einfo-tech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Einfo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_move_template'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/setting.xml',
        'views/financial.xml',
        'views/templates.xml',
        'views/menuitem.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}