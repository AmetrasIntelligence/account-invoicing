{
    "name": """Account Move Line Deep Sort""",
    "summary": """Account Move Line Deep Sort""",
    "version": "13.0.1.0.0",
    "category": "Invoice Management",
    "author": "Ametras intelligence GmbH, Odoo Community Association (OCA) ",
    "website": "https://github.com/OCA/account-invoicing",
    "depends": ["account"],
    "external_dependencies": {"python": ["natsort"]},
    "data": ["views/res_config_settings_views.xml", "views/account_move_views.xml"],
    "installable": True,
    "license": "AGPL-3",
}
