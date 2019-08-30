# -*- coding: utf-8 -*-
{
    'name': "fleet_hours_managing",

    'summary': """
        Implementation of hours on vehicle and lot services for intervention""",

    'description': """
         Implementation of hours on vehicle and lot services for intervention.
		 Each vehicle has his components and their expected life. the use of vehicle is enter daily 
		 for each out of vehicle etc.
    """,

    'author': "AOS SARL",
    

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '12.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fleet','maintenance','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
	'installable': True,
}