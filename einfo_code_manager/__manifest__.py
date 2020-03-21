{
    "name": "einfo code manager",
    "summary": "易捷讯统一管理内部编号",
    "version": "12.0.2.0.0",
    "category": "",
    "license": "LGPL-3",
    "author": "hsp",
    "website": "https://www.einfo-tech.com",
    "depends": [
        "base",
    ],
    "data": [
        "security/res.groups.xml",
        "views/view.xml",
        "security/ir.model.access.csv",
        "views/template.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "external_dependencies": {
        # "python": ['py3o.template',],
        # "bin": [],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}
