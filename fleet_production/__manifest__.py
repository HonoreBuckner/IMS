{
    'name': 'Fleet Production',
    'version': '18.0.1.0',
    'summary': 'Record the time of vehicle worked, create a sale order of worked hours ok',
    'description': 'record vehicle worked hours daily, ',
    'category': 'Category',
    'author': 'AOS Mali',
    'website': 'aosmali.com',
    'license': 'LGPL-3',
    'depends': ['fleet', 'sale','hr_maintenance'],
    'data':["views/fleet_production_view.xml", "security/fleet_production_security.xml"],
    'installable': True,
    'auto_install': False
}

