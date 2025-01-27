# -*- coding: utf-8 -*-
{
    'name': "CryptoProcessor ",

    'summary': """ We are a Cryptocurrency Payment Processor that integrates with Odoo applications. Our Crypto Payment Gateway can do Subscription and recurring billing with Cryptocurrency. We have Bitcoin , Ethereum , Doge , Dash , Litecoin payment gateways and adding coins and tokens.  BTC , ETH , USDT , LTC , DASH , DOGE. Our Crypto checkout for pos integrates seamlessly with Odoo. We are a Digital Currency payment solution, Bitcoin Merchant services provider that has secure crypto transactions so accept crypto payments on your POS now.
•  How to Accept Bitcoin on Odoo Pos
•  Best Crypto Payment Gateway for Odoo
•  Enable Crypto Payments in Odoo pos
•  Easy Bitcoin Payment Integration for Pos
•  Manage Invoices with Cryptocurrency in Odoo
•  Accept Cryptocurrency for Recurring Payments
•  Affordable Crypto Payment Gateway for pos
•  Odoo Integration for Blockchain Payments
•  Best Invoicing Software with Crypto Support
•  Secure Crypto Payments for Pos Businesses
* Low-Cost Crypto Payments
•  Fast Cryptocurrency Transactions
•  Zero Chargeback Risk Payment System
•  Global Payments with Crypto
•  Secure Blockchain Payment Gateway
•  Multi-Currency Crypto Gateway
•  Accept Stablecoins in pos
•  No Middleman Crypto Transactions
•  User-Friendly Crypto Payment Gateway
•  Odoo Crypto Payment Gateway
•  Odoo Cryptocurrency Integration
•  Odoo Bitcoin Payments
•  Accept Crypto in Odoo pos
•  Odoo Blockchain Payment Integration
•  Odoo Crypto Invoicing Solution
•  Odoo Bitcoin Invoices
•  Odoo pos Crypto Payments
•  Odoo POS Cryptocurrency Payments
•  Odoo ERP Crypto Payment Gateway
•  Crypto Payments for Pos Stores
•  pos Cryptocurrency Integration
•  Accept Bitcoin for stores
•  Blockchain Payments for pos
•  Crypto Checkout Solution
•  Bitcoin pos Payment Gateway
•  Crypto Payment Integration for Pos
•  Secure Digital Payments for pos
•  Crypto-Friendly pos
•  Seamless Cryptocurrency Checkout
•  Crypto Invoicing Software
•  Cryptocurrency Invoice Payments
•  Generate Crypto Invoices
•  Bitcoin Invoice Payment Solution
•  Invoice Management with Crypto
•  Accept Ethereum for Invoices
•  Blockchain Invoicing Software
•  Crypto-Friendly Invoice System
•  Recurring Payments with Crypto
•  Invoice Automation with Bitcoin
""",

    'description': """
                We are a Cryptocurrency Payment Processor that integrates with Odoo applications. Our Crypto Payment Gateway can do Subscription and recurring billing with Cryptocurrency. We have Bitcoin , Ethereum , Doge , Dash , Litecoin payment gateways and adding coins and tokens.  BTC , ETH , USDT , LTC , DASH , DOGE. Our Crypto checkout for pos integrates seamlessly with Odoo. We are a Digital Currency payment solution, Bitcoin Merchant services provider that has secure crypto transactions so accept crypto payments on your POS now.
•  How to Accept Bitcoin on Odoo Pos
•  Best Crypto Payment Gateway for Odoo
•  Enable Crypto Payments in Odoo pos
•  Easy Bitcoin Payment Integration for Pos
•  Manage Invoices with Cryptocurrency in Odoo
•  Accept Cryptocurrency for Recurring Payments
•  Affordable Crypto Payment Gateway for pos
•  Odoo Integration for Blockchain Payments
•  Best Invoicing Software with Crypto Support
•  Secure Crypto Payments for Pos Businesses
* Low-Cost Crypto Payments
•  Fast Cryptocurrency Transactions
•  Zero Chargeback Risk Payment System
•  Global Payments with Crypto
•  Secure Blockchain Payment Gateway
•  Multi-Currency Crypto Gateway
•  Accept Stablecoins in pos
•  No Middleman Crypto Transactions
•  User-Friendly Crypto Payment Gateway
•  Odoo Crypto Payment Gateway
•  Odoo Cryptocurrency Integration
•  Odoo Bitcoin Payments
•  Accept Crypto in Odoo pos
•  Odoo Blockchain Payment Integration
•  Odoo Crypto Invoicing Solution
•  Odoo Bitcoin Invoices
•  Odoo pos Crypto Payments
•  Odoo POS Cryptocurrency Payments
•  Odoo ERP Crypto Payment Gateway
•  Crypto Payments for Pos Stores
•  pos Cryptocurrency Integration
•  Accept Bitcoin for stores
•  Blockchain Payments for pos
•  Crypto Checkout Solution
•  Bitcoin pos Payment Gateway
•  Crypto Payment Integration for Pos
•  Secure Digital Payments for pos
•  Crypto-Friendly pos
•  Seamless Cryptocurrency Checkout
•  Crypto Invoicing Software
•  Cryptocurrency Invoice Payments
•  Generate Crypto Invoices
•  Bitcoin Invoice Payment Solution
•  Invoice Management with Crypto
•  Accept Ethereum for Invoices
•  Blockchain Invoicing Software
•  Crypto-Friendly Invoice System
•  Recurring Payments with Crypto
•  Invoice Automation with Bitcoin
    """,

   'author': "Crypto Processor",
    'website': "https://www.cryptoprocessor.ai/",

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

