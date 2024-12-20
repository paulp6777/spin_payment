# -*- coding: utf-8 -*-
{
    'name': "Elavon Payment Gateway Integration",

    'summary': "Elavon Payment converge hosted payment gateway integration for Odoo Website , subscription billing , subscription payments , online Invoicing , Ecommerce , Digital Invoice with payment link , tokenization , mobile payments, recurring payments , buy button , omni commerce payment solution ,  surcharge program option in USA , CANADA , BNPL (Buy Now Pay Later) Avvance integrated to online checkout. Shopping Cart , E-com , e commerce , pos , point of sale system , credit card processing , Debit ,  PayPal , Apple Pay , Google Pay, online payments processing , Payment plugins , payment api , cross-border payments .",

    'description': """
        Elavon Payment converge hosted payment gateway integration for Odoo Website , subscription billing , subscription payments , online Invoicing , Ecommerce , Digital Invoice with payment link , tokenization , mobile payments, recurring payments , buy button , omni commerce payment solution ,  surcharge program option in USA , CANADA , BNPL (Buy Now Pay Later) Avvance integrated to online checkout. Shopping Cart , E-com , e commerce , pos , point of sale system , credit card processing , Debit ,  PayPal , Apple Pay , Google Pay, online payments processing , Payment plugins , payment api , cross-border payments . .
    """,

    'author': "Intruxt Merchant services",
    'website': "http://www.intruxtmerchantservices.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['payment', 'website_sale', 'sale'],

    # always loaded
    'data': [  
        'security/ir.model.access.csv',       
       'views/payment_elavon_templates.xml',
        'views/payment_provider_views.xml',
         'wizard/wizard_return_view.xml',
         'wizard/wizard_capture_view.xml',
         'wizard/wizard_installment_view.xml',
         'data/payment_provider_data.xml',   
         
         'wizard/wizard_recurring_payment_view.xml',
         'views/sale_order_view.xml',
         'views/website_template_view.xml',
         'views/payment_transaction_view.xml',
         
            
    ],
    'images': ['static/description/img/banner.jpeg'],
    'assets': {
        'web.assets_frontend': [
         'payment_elavon/static/src/js/elavon_payment.js',
    ]
    },
    #'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
    'price': 199.00,
    'currency': 'USD'

}

