# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime,timedelta
import pprint
import json
import requests

from hashlib import sha512
import xmltodict ,json
from werkzeug import urls
from urllib.parse import urlparse,urljoin

from odoo import _, api, models, fields
from odoo.exceptions import UserError, ValidationError

from odoo.addons.payment import utils as payment_utils
#from odoo.addons.vm_crypto_payment import const
#from odoo.addons.vm_crypto_payment.controllers.controllers import ElavonPayController
from dateutil.relativedelta import relativedelta

#AMOUNT=1000~APP_ID=1000221129001154~CURRENCY_CODE=840~CUST_CITY=Winterfell~CUST_COUNTRY=US~CUST_EMAIL
#=johnsnow@test.com~CUST_NAME=John Snow~CUST_PHONE=9454243567~CUST_STREET_ADDRESS1=Great Wall~CUST_ZIP=32546
# ~ORDER_ID=7773428492547592~RETURN_URL=https://www.merchant.com/response.jsp~TXNTYPE=SALE


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'


    hash_code=fields.Char('Hash Code')


    def generate_status_hash(self,params):
        params_string = []
        secret_key ='04f02cc0cee14679'
        print("8888888888",secret_key)
        for key in sorted(params.keys()):
            value = '='.join([str(key), str(params[key])])
            params_string.append('' if value == 'null' else str(value))
        
        # Join all values in single string
        params_string = '~'.join(params_string)

        # Add Salt
        final_string ='%s%s' % (params_string, secret_key)
        print('final_stringfinal_string',final_string)
        # Generate 256 hash
        hasher = sha512(final_string.encode())
        hash_string = hasher.hexdigest().upper()
        print("Hash code status",hash_string)
        return hash_string

    def action_crypto_status(self):
        print("Crypto Status Cron")
        pending_transactions = self.search([
            ('state', '=', 'pending'),
            ('provider_reference', '!=', False)])  
        print("pending_transactions",pending_transactions)     
        if pending_transactions:#self.reference and self.state =='pending' and self.provider_reference:
            print("record status", self.id)
            for trans in pending_transactions:
                url="http://sandbox.cryptoprocessor.ai/pgui/services/paymentServices/transactionStatus"
                hash_request ={
                     "APP_ID":trans.provider_id.app_id,
                     "ORDER_ID":trans.reference,
                     "CURRENCY_CODE":trans.currency_id.currency_numeric_code,
                     "AMOUNT":int(trans.amount),
                     "TXN_ID":trans.provider_reference,
                    }
                hash_code=self.generate_status_hash(hash_request)

                payload={
                    
                    "APP_ID":trans.provider_id.app_id,
                    "ORDER_ID":trans.reference,
                    "CURRENCY_CODE":trans.currency_id.currency_numeric_code,
                    "AMOUNT":int(trans.amount),
                    "TXN_ID":trans.provider_reference,
                    "HASH":hash_code
                    }
                print("status payload",payload )
                response = requests.post(url, json = payload)

                res=json.loads(response.text)
                print("Status1111111111 ",response,type(res))
                print("Statu333333333333333333311 ",response,type(res[0]))
                response_code=''
                response_message=''
                if  'RESPONSE_CODE' in res[0]:
                    print("RESPONSE_CODERESPONSE_CODE44")
                    response_code=res[0]['RESPONSE_CODE']
                    response_message=res[0]['CRYPTO_DEPOSIT_ADDRESS']
                    print("response_code",response_code)
                    if response_code =='000':
                        trans._set_done()
                    else:
                        _logger.warning(
                            "Received data with invalid success code (%s) for transaction with primary response "
                            "code %s and reference %s.", response_code, response_message, trans.reference
                        )
                        trans._set_error("Crypto_Pay: " + _("Unknown success code and response: %s %s", response_code,response_message))

               
                elif response_code =="015" and  notification_data.get('TXNTYPE') =='SALE':
                    print("pending")
                    trans.provider_reference=notification_data.get('TXN_ID')
                    trans._set_pending()
                    #self._set_canceled()            
                else:
                    _logger.warning(
                        "Received data with invalid success code (%s) for transaction with primary response "
                        "code %s and reference %s.", response_code, response_message, trans.reference
                    )
                    self._set_error("Crypto_Pay: " + _("Unknown success code: %s", response_code))
        else:
                _logger.warning(
                    "Received data with invalid success code (%s) for transaction with primary response "
                   
                )
                self._set_error("Crypto_Pay: " + _("Unknown success code"))



           

    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator='-', **kwargs):
        """ Override of `payment` to ensure that AsiaPay requirements for references are satisfied.

        AsiaPay requirements for references are as follows:
        - References must be unique at provider level for a given merchant account.
          This is satisfied by singularizing the prefix with the current datetime. If two
          transactions are created simultaneously, `_compute_reference` ensures the uniqueness of
          references by suffixing a sequence number.
        - References must be at most 35 characters long.

        :param str provider_code: The code of the provider handling the transaction.
        :param str prefix: The custom prefix used to compute the full reference.
        :param str separator: The custom separator used to separate the prefix from the suffix.
        :return: The unique reference for the transaction.
        :rtype: str
        """
        if provider_code != 'crypto':
            return super()._compute_reference(provider_code, prefix=prefix, **kwargs)

        if not prefix:
            # If no prefix is provided, it could mean that a module has passed a kwarg intended for
            # the `_compute_reference_prefix` method, as it is only called if the prefix is empty.
            # We call it manually here because singularizing the prefix would generate a default
            # value if it was empty, hence preventing the method from ever being called and the
            # transaction from received a reference named after the related document.
            prefix = self.sudo()._compute_reference_prefix(provider_code, separator, **kwargs) or None
        prefix = payment_utils.singularize_reference_prefix(prefix=prefix, max_length=35)
        return super()._compute_reference(provider_code, prefix=prefix, **kwargs)

    def generate_hash(self,params):
        params_string = []
        secret_key ='04f02cc0cee14679'
        print("777777777",secret_key)
        for key in sorted(params.keys()):
            value = '='.join([str(key), str(params[key])])
            params_string.append('' if value == 'null' else str(value))
        
        # Join all values in single string
        params_string = '~'.join(params_string)

        # Add Salt
        final_string = '%s%s' % (params_string, secret_key)
        print('final_stringfinal_string',final_string)
        # Generate 256 hash
        hasher = sha512(final_string.encode())
        hash_string = hasher.hexdigest().upper()
        print("hash_stringhash_stringhash_stringhash_string",hash_string)
        return hash_string

    def _get_specific_rendering_values(self, processing_values):
        print("_get_specific_rendering_values",processing_values)
        """ Override of `payment` to return AsiaPay-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`.

        :param dict processing_values: The generic and specific processing values of the
                                       transaction.
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        def get_language_code(lang_):
            """ Return the language code corresponding to the provided lang.

            If the lang is not mapped to any language code, the country code is used instead. In
            case the country code has no match either, we fall back to English.

            :param str lang_: The lang, in IETF language tag format.
            :return: The corresponding language code.
            :rtype: str
            """
            language_code_ = const.LANGUAGE_CODES_MAPPING.get(lang_)
            if not language_code_:
                country_code_ = lang_.split('_')[0]
                language_code_ = const.LANGUAGE_CODES_MAPPING.get(country_code_)
            if not language_code_:
                language_code_ = const.LANGUAGE_CODES_MAPPING['en']
            return language_code_

        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'crypto':
            return res
        print ("processing_values",processing_values, res)
        base_url = self.provider_id.get_base_url()
        RETURN_URL='%s' % urljoin(base_url,'/payment/crypto/success')
        #RETURN_URl="http://127.0.0.27:9027/payment/crypto/success"
        data = {}        
        AMOUNT=int(self.amount)       
        data["AMOUNT"] =AMOUNT
        data["APP_ID"] = self.provider_id.app_id
        data["CURRENCY_CODE"] = self.currency_id.currency_numeric_code
        data["CUST_CITY"] = self.partner_id.city
        data["CUST_COUNTRY"]=self.partner_id.country_id.code
        data["CUST_EMAIL"] = self.partner_id.email
        data["CUST_NAME"] = self.partner_id.name
        data["CUST_PHONE"] = self.partner_id.phone  or self.partner_id.mobile 
        data["CUST_STATE"]=self.partner_id.state_id.name
        data["CUST_STREET_ADDRESS1"] =self.partner_id.street   
        data["CUST_ZIP"] = self.partner_id.zip
        data["ORDER_ID"] = self.reference
        data["RETURN_URL"] = RETURN_URL
        data["TXNTYPE"] = self.provider_id.crypto_transaction_type
        data["PRODUCT_DESC"]="testproduct"
        
        
        rendering_values = {
                "api_url":self.provider_id._crypto_get_api_url()['api_url'],
                "APP_ID":self.provider_id.app_id,
                "ORDER_ID":self.reference,
                "TXNTYPE":self.provider_id.crypto_transaction_type,
                "CURRENCY_CODE":self.currency_id.currency_numeric_code,
                "CUST_NAME":self.partner_id.name,
                "CUST_STREET_ADDRESS1":self.partner_id.street ,
                "CUST_ZIP":self.partner_id.zip,        
                "CUST_PHONE":self.partner_id.phone  or self.partner_id.mobile ,
                "CUST_EMAIL":self.partner_id.email,        
                "AMOUNT":AMOUNT,        
                "RETURN_URL":RETURN_URL,
                "HASH":self.generate_hash(data),
                "PRODUCT_DESC":"testproduct",
                "CUST_STATE":self.partner_id.state_id.name,
                "CUST_CITY":self.partner_id.city,
                "CUST_COUNTRY":self.partner_id.country_id.code

            
        }
        print("rendering_values 11111111",rendering_values)
        
        return rendering_values

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        print("_get_tx_from_notification_data",provider_code, notification_data)
        """ Override of `payment` to find the transaction based on AsiaPay data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction if found.
        :rtype: recordset of `payment.transaction`
        :raise ValidationError: If inconsistent data are received.
        :raise ValidationError: If the data match no transaction.
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'crypto' or len(tx) == 1:
            return tx

        reference = notification_data.get('ORDER_ID')
        
        if not reference:
            raise ValidationError(
                "Elavon_Pay: " + _("Payment canclled by User %(ref)s.", ref=reference)
            )
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'crypto')])
       
        if not tx:
            raise ValidationError(
                "Elavon_Pay: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _get_specific_processing_values(self, processing_values):
        print("_get_specific_processing_values",processing_values)
        """ Override of payment to return an access token as provider-specific processing values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'crypto':
            return res

        return {
            'access_token': payment_utils.generate_access_token(
                processing_values['reference'], processing_values['partner_id']
            )
        }


    def _process_notification_data(self, notification_data):
        print("_process_notification_data", notification_data)
        """ Override of payment to process the transaction based on Mollie data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'crypto':
            return
        print("notification_data",notification_data)
        response_code = notification_data.get('RESPONSE_CODE')
        response_message = notification_data.get('RESPONSE_MESSAGE')
        print("response_message code ",response_code, response_message)
        if not response_code:
            raise ValidationError("Crypto_Pay: " + _("Received data with missing success code."))
        elif response_code =="000" and notification_data.get('TXNTYPE') =='SALE':
            print("sale")
            self.provider_reference=notification_data.get('TXN_ID')
            self.hash_code=notification_data.get('HASH')
            self._set_done()
            #self._set_pending()
        elif response_code =="015" and  notification_data.get('TXNTYPE') =='SALE':
            print("pending")
            self.provider_reference=notification_data.get('TXN_ID')
            self._set_pending()
            #self._set_canceled() 
        elif response_code =="000" and notification_data.get('TXNTYPE') =='AUTH':
            print("Auth")
            self.provider_reference=notification_data.get('TXN_ID')
            self._set_authorized()           
        else:
            _logger.warning(
                "Received data with invalid success code (%s) for transaction with primary response "
                "code %s and reference %s.", response_code, response_message, self.reference
            )
            self._set_error("Crypto_Pay: " + _("Unknown success code: %s", response_code))




   