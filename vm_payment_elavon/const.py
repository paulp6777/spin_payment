# Part of Odoo. See LICENSE file for full copyright and licensing details.

API_URLS = {
    'production': {
        'elavon': 'https://api.convergepay.com/hosted-payments/transaction_token',
       
    },
    'test': {
        'elavon': 'https://api.demo.convergepay.com/hosted-payments/transaction_token',
       
    },

    'process_test': {
        'test': 'https://api.convergepay.com/VirtualMerchantDemo/processxml.do',
       
    },

    'process_live': {
        'live': 'https://api.convergepay.com/VirtualMerchant/processxml.do'#'https://api.convergepay.com/VirtualMerchantDemo/processxml.do',
       
    },



}


# Mapping of both country codes (e.g., 'es') and IETF language tags (e.g.: 'fr-BE') to AsiaPay
# language codes. If a language tag is not listed, the country code prefix can serve as fallback.
LANGUAGE_CODES_MAPPING = {
    'en': 'E',
    'zh_HK': 'C',
    'zh_TW': 'C',
    'zh_CN': 'X',
    'ja_JP': 'J',
    'th_TH': 'T',
    'fr': 'F',
    'de': 'G',
    'ru_RU': 'R',
    'es': 'S',
    'vi_VN': 'S',
}

DEFAULT_PAYMENT_METHODS_CODES = [
    # Primary payment methods.
    'card',
    # Brand payment methods.
    'visa',
    'mastercard',
]

# Mapping of payment method codes to AsiaPay codes.
PAYMENT_METHODS_MAPPING = {

'mastercard': 'MC',
}
