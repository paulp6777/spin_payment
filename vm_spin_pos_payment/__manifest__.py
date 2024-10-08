# -*- coding: utf-8 -*-
{
    'name': "Spin Payment Terminal Integration",

    'summary': "DejaVoo Pos Spin Payment terminal integration for Odoo , multi location management , inventory management , with surcharge program and Dual Pricing , Cash Discount options in USA , CANADA .  Nuvei  payment processing for  Z8 , Z9 , Z11 , pos software , payment gateway integration , Credit Card machine , credit card processing ,  Debit , interac ,  PayPal , Apple Pay , Google Pay integrated to Point of Sale and invoicing like restaurant and retail applications. POS system integration.",

    'description': """
DejaVoo Pos Spin Payment terminal integration for Odoo , multi location management , inventory management , with surcharge program and Dual Pricing , Cash Discount options in USA , CANADA .  Nuvei  payment processing for  Z8 , Z9 , Z11 , pos software , payment gateway integration , Credit Card machine , credit card processing ,  Debit , interac ,  PayPal , Apple Pay , Google Pay integrated to Point of Sale and invoicing like restaurant and retail applications. POS system integration..
    """,

    'author': "Intruxt Merchant services",
    'website': "http://www.intruxtmerchantservices.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'POS',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/spin_pos_payment_view.xml',
        'views/pos_payment_method_views.xml',
        'views/spin_pos_terminal_payments_views.xml',
        'wizard/wizard_pos_make_payment_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
      #  'demo/demo.xml',
    ],

    'images': ['static/description/img/z9.jpeg','static/description/img/z11.jpeg'],
    'assets': {
        'point_of_sale._assets_pos': [
            'vm_spin_pos_payment/static/**/*',
        ],
    },
     'license': 'LGPL-3',
    'price': 199.00,
     'currency': 'USD'
}
