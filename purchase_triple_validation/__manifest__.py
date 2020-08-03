# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Triple Validation',
    'version': '1.0',
    'category': 'Purchases',
    'sequence': 70,
    'summary': 'Triple validation for Purchase Orders ',
    'description': "",
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'security/purchase_triple_validation_security.xml',
        'views/triple_purchase_views.xml',
        'wizard/purchase_refuse_reason_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
