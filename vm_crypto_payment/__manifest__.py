# -*- coding: utf-8 -*-
{
    'name': "CryptoProcessor ",

    'summary': "CryptoProcessor.ai Integration with Odoo Website",

    'description': """
                CryptoProcessor.ai provides a cryptocurrency payment option for businesses.
                Customers can make payments using popular cryptocurrencies using the CryptoProcessor.ai
                gateway through Odoo website for ecommerce and invoice and subscription or recurring
                payments
    """,

   'author': "Intruxt Merchant services",
    'website': "http://www.intruxtmerchantservices.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'payment','website_sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        
        'views/payment_provider_views.xml',
        'views/payment_crypto_templates.xml',
        'data/payment_provider_data.xml',
        'views/payment_transaction_view.xml',
        'views/res_currency_view.xml',
        'data/crypto_payment_status.xml'
    ],
   'images': ['static/description/img/banner.jpeg'],
    'external_dependencies': {
        'python' : ['xmltodict'],
    },

    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
    'price': 50.00,
    'currency': 'EUR'
}

