# -*- coding: utf-8 -*-
{
    'name': "柯沃项目管理体系流程",

    'summary': """
     柯沃项目管理体系流程""",

    'description': """
     待补充
    """,

    'author': "Einfo-Tech",
    'website': "http://www.einfo-tech.com",
    'category': 'Tools',
    'version': '1.0',

    'depends': ['base','mail','hr','account','purchase','stock','web_tree_dynamic_colored_field','einfo_code_manager'],  #,'ps_purchase','purchase_requisition'

    'data': [
        "views/cowork_project_priority.xml",
        "views/cowork_project_difficulty.xml",
        "views/cowork_project_apply.xml",
        "views/cowork_project_estimate.xml",
        "views/cowork_scheme_preliminary.xml",
        "views/cowork_cost_material.xml",
        "views/cowork_material_class.xml",
        "views/cowork_material_category.xml",
        "views/cowork_cost_material_detail_line.xml",
        "views/product_brand.xml",
        "views/cowork_quote_order.xml",
        "views/cowork_bom.xml",
        "views/work.xml",
        "views/cowork_purchase_order.xml",
        "views/cowork_purchase_order_line.xml",
        "views/wizard.xml",
        "security/groups_config.xml",
        "security/ir.model.access.csv",
        "views/menu.xml",
        "data/cowork_project_difficulty.xml",
        "data/cowork_project_priority.xml",
        "data/cowork_material_category.xml",
        "data/cowork_material_class.xml",
    ],

    'installable':True,
    'application':True,

}