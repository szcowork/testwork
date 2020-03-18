# -*- coding: utf-8 -*-
##############################################################################
{
    "name": "einfo 自定义审批流",
    "version": "12",
    'license': 'OPL-1',
    "website": "",
    "depends": ["base", "web", "purchase", "calendar"],
    "author": "<Jon alangwansui@qq.com>",
    "category": "Tools",
    "description": """
       A Powerful Custom Workflow Tool. Very easy to create and update Workflow!
    """,
    'external_dependencies': {
        'python': [
            'pyutillib',
        ],
    },
    'demo': [
        'demo/wkf.base.csv',
        'demo/wkf.node.csv',
        'demo/wkf.trans.csv',
    ],
    # 'qweb': ['static/src/xml/*.xml'],
    "data": [
        'security/ir.model.access.csv',
        'views/wkf.xml',
        'wizard/wizard_wkf.xml',
    ],
    'installable': True,
    'active': True,
    # 'price': 99,
    # 'currency': 'EUR',
    'auto_install': True,
    'images': [
        'static/description/theme.jpg',
    ],

}
