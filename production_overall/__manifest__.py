# -*- coding: utf-8 -*-
{
    'name': "production_overall",

    'summary': """
        Production""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Viltco",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mrp', 'stock', 'material_purchase_requisitions'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/production_view.xml',
        'views/picking_views.xml',
        'views/requisition_views.xml',
    ],

}
