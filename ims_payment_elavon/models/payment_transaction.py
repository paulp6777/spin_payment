# Part of Odoo. See LICENSE file for full copyright and licensing details.



#5121212121212124
import logging
from datetime import datetime,timedelta
import pprint

import requests

import xmltodict ,json
from werkzeug import urls

from odoo import _, api, models, fields
from odoo.exceptions import UserError, ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.ims_payment_elavon import const
from odoo.addons.ims_payment_elavon.controllers.controllers import ElavonPayController
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'


    ssl_txn_id=fields.Char('Elavon ssl_txn_id')
    state = fields.Selection(selection_add=[('delete', "Delete")], ondelete={'delete': 'set default'} )

    ssl_billing_cycle=fields.Selection([('DAILY','DAILY'),('BIWEEKLY','BIWEEKLY'),('SEMIMONTHLY','SEMIMONTHLY'),
                    ('MONTHLY','MONTHLY'),('BIMONTHLY','BIMONTHLY'),('QUARTERLY','QUARTERLY'),('SEMESTER','SEMESTER'),
                    ('SUSPENDED','SUSPENDED')], string=" Installement Billing Cycle")
    recurring=fields.Selection([('yes','Yes'),('no','NO')],default='no')
    ssl_next_payment_date=fields.Date('Next Payment Date', compute='next_payment_date')
    installment_option=fields.Selection([('yes','Yes'),('no','NO')],default='no')
    recurring_active=fields.Boolean('Recurring Active')
    installment_active=fields.Boolean('Installment Active')
    ssl_total_installments=fields.Selection([('3','3'),('4','4'),('5','5'), ('6','6'),('7','7'),('8','8'),('9','9'), ('10','10'),('11','11'),('12','12')], string="Total Installment")


    @api.depends('ssl_billing_cycle','recurring')
    def next_payment_date(self):
        for rec in self:
            if rec.ssl_billing_cycle and rec.recurring:
                if rec.ssl_billing_cycle == 'DAILY':
                    rec.ssl_next_payment_date =rec.create_date + relativedelta(days=1)

                elif rec.ssl_billing_cycle =='BIWEEKLY':
                    rec.ssl_next_payment_date =rec.create_date +  relativedelta(days=7)

                elif rec.ssl_billing_cycle =='SEMIMONTHLY':
                    rec.ssl_next_payment_date =rec.create_date +  relativedelta(days=15)

                elif rec.ssl_billing_cycle =='MONTHLY':
                    rec.ssl_next_payment_date =rec.create_date +  relativedelta(days=30)

                elif rec.ssl_billing_cycle =='BIMONTHLY':
                    rec.ssl_next_payment_date =rec.create_date +  relativedelta(days=60)

                elif rec.ssl_billing_cycle =='QUARTERLY':
                    rec.ssl_next_payment_date =rec.create_date +  relativedelta(days=90)

                elif rec.ssl_billing_cycle =='SEMESTER':
                    rec.ssl_next_payment_date =rec.create_date +  relativedelta(days=180)

                elif rec.ssl_billing_cycle =='SUSPENDED':
                    rec.ssl_next_payment_date =rec.create_date +  relativedelta(days=2)


                else:
                    rec.ssl_next_payment_date =''
            else:
                rec.ssl_next_payment_date =''



    def create(self,vals):

        res=super().create(vals)
        print("bbb",res.sale_order_ids)
        if res.sale_order_ids:
            for sale_id in res.sale_order_ids:
                res.ssl_billing_cycle=sale_id.ssl_billing_cycle
                res.recurring=sale_id.recurring
                res.installment_option=sale_id.installment_option
                res.ssl_total_installments=sale_id.ssl_total_installments

        print("createcreatecreate",res,vals)

        return res



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
        if provider_code != 'elavon':
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
        if self.provider_code != 'elavon':
            return res
        print ("processing_values",processing_values, res)

        base_url = self.provider_id.get_base_url()
        # The lang is taken from the context rather than from the partner because it is not required
        # to be logged in to make a payment, and because the lang is not always set on the partner.
        lang = self._context.get('lang') or 'en_US'
        base_url = self.provider_id.get_base_url()
        rendering_values = {
            'ssl_merchant_id': self.provider_id.ssl_merchant_id,
            'ssl_user_id':self.provider_id.ssl_user_id,
            'ssl_pin':self.provider_id.ssl_pin,
            'ssl_amount': self.amount,
            'ssl_invoice_number': self.reference,
            'ssl_transaction_type':self.provider_id.ssl_transaction_type,
            "ssl_first_name":self.partner_id.name,
            "ssl_last_name":self.partner_id.name,
            "ssl_email":self.partner_id.email,
            "ssl_company":self.partner_id.company_name,
            "ssl_avs_address":self.partner_id.street2,
            "ssl_address2":self.partner_id.street,
            "ssl_ship_to_address1":self.partner_id.street,
            "ssl_city":self.partner_id.city,
            "ssl_state":self.partner_id.state_id.name,
            "ssl_avs_zip":self.partner_id.zip,
            "ssl_phone":self.partner_id.phone if self.partner_id.phone else self.partner_id.mobile,
            "ssl_country":self.partner_id.country_id.name,
            'ssl_callback_url':urls.url_join(base_url, ElavonPayController._return_url),
            "ssl_add_token":"Y",
            "ssl_get_token":"Y",
            "id_same_as_billing":"Y"

           # "ssl_token":"5470052779992124"

            #'currency_code': const.CURRENCY_MAPPING[self.provider_id.available_currency_ids[0].name],
            # 'mps_mode': 'SCP',
            # 'return_url': urls.url_join(base_url, AsiaPayController._return_url),
            # 'payment_type': 'N',
            # 'language': get_language_code(lang),
            # 'payment_method': const.PAYMENT_METHODS_MAPPING.get(self.payment_method_id.code, 'ALL'),
        }
        #url https://api.convergepay.com/hosted-payments/transaction_token
        url =self.provider_id._elavon_get_api_url() #'https://api.demo.convergepay.com/hosted-payments/transaction_token'##'https://api.demo.convergepay.com/hosted-payments/transaction_token'
        myobj = {

         "ssl_merchant_id":self.provider_id.ssl_merchant_id,#"0022742",
         "ssl_user_id":self.provider_id.ssl_user_id,#"apiuser",
         "ssl_pin":self.provider_id.ssl_pin,#"YA8P237WMBGE2VUNWOJXLCXKB7EL809M4W6PGUVR8O753C5GZNCBU6SAHNAB4HIR",
         "ssl_transaction_type":self.provider_id.ssl_transaction_type,
         "ssl_amount":str(self.amount),
         "ssl_add_token":"Y",
         "ssl_get_token":"Y",
         # "ssl_base_amount":str(self.amount),
         # "ssl_tip_amount":12.00,
         # "ssl_server":"34567834"

        
           
        }
        print("url", url, myobj)

        x = requests.post(url, json = myobj)
        print("2222", x)
        rendering_values.update({
            # 'secure_hash': self.provider_id._asiapay_calculate_signature(
            #     rendering_values, incoming=False
            # ),
            'api_url':const.API_URLS['elavon_token_live']['token_live'] if self.provider_id.state =='enabled'  else const.API_URLS['elavon_token_test']['token_test']+str(x.text)#'https://api.convergepay.com/hosted-payments?ssl_txn_auth_token='+str(x.text) #self.provider_id._elavon_get_api_url()
        })
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
        if provider_code != 'elavon' or len(tx) == 1:
            return tx

        reference = notification_data.get('ssl_invoice_number')
        if not reference:
            raise ValidationError(
                "Elavon_Pay: " + _("Payment canclled by User %(ref)s.", ref=reference)
            )

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'elavon')])
        if not tx:
            raise Elavon_Pay(
                "Elavon_Pay: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _process_notification_data(self, notification_data):
        print("_process_notification_data_process_notification_data",notification_data)
        """ Override of `payment' to process the transaction based on AsiaPay data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data are received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'elavon':
            return

        # Update the provider reference.
        self.provider_reference = notification_data.get('ssl_invoice_number')
        self.ssl_txn_id = notification_data.get('ssl_txn_id')
        #self.tokenize=True
        ssl_transaction_type=notification_data.get('ssl_transaction_type')

        # Update the payment method.
        # payment_method_code = notification_data.get('ssl_card_short_description')
        # payment_method = self.env['payment.method']._get_from_code(
        #     payment_method_code, mapping=const.PAYMENT_METHODS_MAPPING
        # )
        # self.payment_method_id = payment_method or self.payment_method_id

        # Update the payment state.
        success_code = notification_data.get('ssl_result_message')
        primary_response_code = notification_data.get('ssl_result_message')
        print("success_code",success_code, ssl_transaction_type)
        if not success_code:
            raise ValidationError("Elavon_Pay: " + _("Received data with missing success code."))
        elif success_code =="APPROVAL" and ssl_transaction_type =='SALE':
            self._set_done()
            # has_token_data = 'token' in verified_data.get('card', {})
            # if self.tokenize and has_token_data:
            #     self._flutterwave_tokenize_from_notification_data(verified_data)
            print("SSSSSSSSSSSSSSSS")
            ssl_end_of_month='N'
            if self.recurring== 'yes':
                
                self.action_recurring(self.ssl_billing_cycle,ssl_end_of_month, self.ssl_next_payment_date)

            if self.installment_option =='yes':
                no_of_installment=int(self.ssl_total_installments)
                self.elavon_make_installment(round((self.amount/no_of_installment),2),self.ssl_billing_cycle,self.ssl_next_payment_date,ssl_end_of_month,self.ssl_total_installments)
            
            
            if  notification_data.get('ssl_token'):
                print("notification_data.get('ssl_token')",notification_data.get('ssl_token'))
                token_id=self.env['payment.token'].search([('provider_ref','=', notification_data.get('ssl_token'))],limit=1)
                if not token_id:
                    self._elavon_tokenize_from_notification_data(notification_data)
        elif success_code =="APPROVAL" and ssl_transaction_type =='AUTHONLY':
            print("AAAAAAAAAAAAAAAAAAAAAAAAAa")
            self._set_authorized()

        elif success_code =="APPROVAL" and ssl_transaction_type =='COMPLETE':
            print("cccccccccccccccccc")
            self._set_done()
        elif success_code =="APPROVAL" and ssl_transaction_type =='RETURN':
            print("Refund  Refund")
            self._set_done()
        elif success_code =="APPROVAL" and ssl_transaction_type =='VOID':
            print("VOID  VOID")
            self._set_canceled()            
        else:
            _logger.warning(
                "Received data with invalid success code (%s) for transaction with primary response "
                "code %s and reference %s.", success_code, primary_response_code, self.reference
            )
            self._set_error("Elavon_Pay: " + _("Unknown success code: %s", success_code))

    def _elavon_make_capture(self, amount_to_capture):
        print("_elavon_make_capture")
        self.ensure_one()

        url = const.API_URLS['process_live']['live'] if self.provider_id.state =='enabled'  else const.API_URLS['process_test']['test'] #"https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
        payload = '''
                <txn>
                  <ssl_merchant_id>{}</ssl_merchant_id>
                  <ssl_user_id>{}</ssl_user_id>
                  <ssl_pin>{}</ssl_pin>
                  <ssl_transaction_type>cccomplete</ssl_transaction_type>
                  <ssl_txn_id>{}</ssl_txn_id>
                  <ssl_result_format>ascii</ssl_result_format>
                 <ssl_show_form>false</ssl_show_form>
                 <ssl_amount>{}</ssl_amount>
                </txn>
                '''
        headers = {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
        payload=payload.format(self.provider_id.ssl_merchant_id,self.provider_id.ssl_user_id,self.provider_id.ssl_pin,self.ssl_txn_id,amount_to_capture)
        print("Requiest",payload)
        result = requests.post(url, data={'xmldata': payload}, headers=headers)
        print("555",(result.text))
        xml_json = xmltodict.parse(result.content)
        res_json=json.dumps(xml_json)
        response = json.loads(res_json)
        response=response['txn']
    
        return response

        # url ='https://api.demo.convergepay.com/hosted-payments/transaction_token'#self.provider_id._elavon_get_api_url()
        # myobj = {

        #     'ssl_merchant_id': str(self.provider_id.ssl_merchant_id),
        #     'ssl_user_id':str(self.provider_id.ssl_user_id),
        #     'ssl_pin':str(self.provider_id.ssl_pin),
        #     'ssl_transaction_type':'cccomplete',
        #     'ssl_txn_id':str(self.ssl_txn_id),
        #     'ssl_amount':str(self.amount),
        
           
        # }
        # print("url", url, myobj)

        # x = requests.post(url, json = myobj)
        # print("777",x)
        # get_url='https://api.demo.convergepay.com/hosted-payments?ssl_txn_auth_token='+str(x.text)

        # response=requests.get(get_url)

        # return response



    def _send_capture_request(self, amount_to_capture=None):

        print("Elavon _send_capture_request", amount_to_capture)
        """ Override of `payment` to send a capture request to Razorpay. """
        child_capture_tx = super()._send_capture_request(amount_to_capture=amount_to_capture)
        if self.provider_code != 'elavon':
            return child_capture_tx

        converted_amount= payment_utils.to_minor_currency_units(self.amount, self.currency_id)
        print("Elavon _send_capture_request", child_capture_tx)
        payload = {'amount': converted_amount, 'currency': self.currency_id.name}
        _logger.info(
            "Payload of '/payments/<id>/capture' request for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(payload)
        )
        response_content =self._elavon_make_capture(amount_to_capture)
        print("Elavon _send_capture_request 333333", response_content)
        _logger.info(
            "Response of '/payments/<id>/capture' request for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(response_content)
        )

        # Handle the capture request response.
        self._handle_notification_data('elavon', response_content)
        child_capture_tx._handle_notification_data('elavon', response_content)

        return child_capture_tx


    def action_void(self):
        """ Check the state of the transaction and request to have them voided. """
        payment_utils.check_rights_on_recordset(self)

        if any(tx.state not in  ('authorized','done') for tx in self):
            raise ValidationError(_("Only authorized transactions can be voided."))

        for tx in self:
            # Consider all the confirmed partial capture (same operation as parent) child txs.
            captured_amount = sum(child_tx.amount for child_tx in tx.child_transaction_ids.filtered(
                lambda t: t.state == 'done' and t.operation == tx.operation
            ))
            # In sudo mode because we need to be able to read on provider fields.
            tx.sudo()._send_void_request(amount_to_void=tx.amount - captured_amount)




    def _elavon_make_avoid(self):
        print("_elavon_make_avoid")

        self.ensure_one()
        url = const.API_URLS['process_live']['live'] if self.provider_id.state =='enabled'  else const.API_URLS['process_test']['test']#"https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
        payload = '''
                <txn>
                  <ssl_merchant_id>{}</ssl_merchant_id>
                  <ssl_user_id>{}</ssl_user_id>
                  <ssl_pin>{}</ssl_pin>
                  <ssl_transaction_type>ccvoid</ssl_transaction_type>
                  <ssl_txn_id>{}</ssl_txn_id>
                  <ssl_result_format>ascii</ssl_result_format>
                 <ssl_show_form>false</ssl_show_form>
                </txn>
                '''
        headers = {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
        payload=payload.format(self.provider_id.ssl_merchant_id,self.provider_id.ssl_user_id,self.provider_id.ssl_pin,self.ssl_txn_id)
        print("Requiest",payload)
        result = requests.post(url, data={'xmldata': payload}, headers=headers)
        print("555",(result.text))
        xml_json = xmltodict.parse(result.content)
        res_json=json.dumps(xml_json)
        response = json.loads(res_json)
        response=response['txn']
       
        return response

        # url ='https://api.demo.convergepay.com/hosted-payments/transaction_token'#self.provider_id._elavon_get_api_url()
        # myobj = {

        #     'ssl_merchant_id': str(self.provider_id.ssl_merchant_id),
        #     'ssl_user_id':str(self.provider_id.ssl_user_id),
        #     'ssl_pin':str(self.provider_id.ssl_pin),
        #     'ssl_transaction_type':'ccvoid',
        #     'ssl_txn_id':str(self.ssl_txn_id),
        #    # 'ssl_amount':str(self.amount),
        
           
        # }
        # print("url", url, myobj)

        # x = requests.post(url, json = myobj)
        # print("777",x)
        # get_url='https://api.demo.convergepay.com/hosted-payments?ssl_txn_auth_token='+str(x.text)

        # response=requests.get(get_url)

        # return response

    def _send_void_request(self, amount_to_void=None):
        """ Override of payment to send a void request to Authorize. """
        child_void_tx = super()._send_void_request(amount_to_void=amount_to_void)
        print(" elavon _send_void_request")
        if self.provider_code != 'elavon':
            return child_void_tx


        res_content =self._elavon_make_avoid()
        _logger.info(
            "void request response for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(res_content)
        )
        
        child_void_tx._handle_notification_data('elavon', res_content)

        return child_void_tx



    def _elavon_make_refund(self,amount_to_refund):
        print("_elavon_make_refund_elavon_make_refund")
        self.ensure_one()
        url =const.API_URLS['process_live']['live'] if self.provider_id.state =='enabled'  else const.API_URLS['process_test']['test']#"https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
        payload = '''
                <txn>
                  <ssl_merchant_id>{}</ssl_merchant_id>
                  <ssl_user_id>{}</ssl_user_id>
                  <ssl_pin>{}</ssl_pin>
                  <ssl_transaction_type>ccreturn</ssl_transaction_type>
                  <ssl_txn_id>{}</ssl_txn_id>
                  <ssl_result_format>ascii</ssl_result_format>
                 <ssl_show_form>false</ssl_show_form>
                </txn>
                '''
        headers = {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
        print("Refund url",url)
        payload=payload.format(self.provider_id.ssl_merchant_id,self.provider_id.ssl_user_id,self.provider_id.ssl_pin,self.ssl_txn_id)
        print("Requiest",payload)
        result = requests.post(url, data={'xmldata': payload}, headers=headers)
        print("555",type(result.text))
        xml_json = xmltodict.parse(result.content)
        res_json=json.dumps(xml_json)
        response = json.loads(res_json)
        response=response['txn']
        
        return response


    def _send_refund_request(self, amount_to_refund=None):
        print("Elavon _send_refund_request_send_refund_request",amount_to_refund)
        
        """ Override of `payment` to send a refund request to Elavon.

        Note: self.ensure_one()

        :param float amount_to_refund: The amount to refund.
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """
        refund_tx = super()._send_refund_request(amount_to_refund=amount_to_refund)
        print("refund_txrefund_tx",refund_tx)
        if self.provider_code != 'elavon':
            return refund_tx

        # Make the refund request to Elavon.
        converted_amount = payment_utils.to_minor_currency_units(
            -refund_tx.amount, refund_tx.currency_id
        )  # The amount is negative for refund transactions.
        payload = {
            'amount': converted_amount,
            'notes': {
                'reference': refund_tx.reference,  # Allow retrieving the ref. from webhook data.
            },
        }
        _logger.info(
            "Payload of '/payments/<id>/refund' request for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(payload)
        )
        response_content = self._elavon_make_refund(converted_amount)
        print("Refund 5545555", response_content)
        _logger.info(
            "Response of '/payments/<id>/refund' request for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(response_content)
        )
        response_content.update(entity_type='refund')
        refund_tx._handle_notification_data('elavon', response_content)

        return refund_tx


    def _set_canceled(self, state_message=None, extra_allowed_states=()):
        """ Update the transactions' state to `cancel`.

        :param str state_message: The reason for setting the transactions in the state `cancel`.
        :param tuple[str] extra_allowed_states: The extra states that should be considered allowed
                                                target states for the source state 'canceled'.
        :return: The updated transactions.
        :rtype: recordset of `payment.transaction`
        """
        allowed_states = ('draft', 'pending', 'authorized', 'done')
        target_state = 'cancel'
        txs_to_process = self._update_state(
            allowed_states + extra_allowed_states, target_state, state_message
        )
        txs_to_process._update_source_transaction_state()
        txs_to_process._log_received_message()
        return txs_to_process


    def _set_delete_state(self):
        print("self.sale_order_ids",self.sale_order_ids)
        if self.sale_order_ids:
            self.sale_order_ids._action_cancel()

            # for sale in self.sale_order_ids:
            #     sale.action_cancel()
        self.state='delete'


    def action_delete(self):
        print("action_delete")
        self.ensure_one()

        url = const.API_URLS['process_live']['live'] if self.provider_id.state =='enabled'  else const.API_URLS['process_test']['test']#"https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
        payload = '''
                <txn>
                  <ssl_merchant_id>{}</ssl_merchant_id>
                  <ssl_user_id>{}</ssl_user_id>
                  <ssl_pin>{}</ssl_pin>
                  <ssl_transaction_type>ccdelete</ssl_transaction_type>
                  <ssl_txn_id>{}</ssl_txn_id>
                  
                </txn>
                '''
        headers = {
              'Content-Type': 'application/x-www-form-urlencoded'
            }
        payload=payload.format(self.provider_id.ssl_merchant_id,self.provider_id.ssl_user_id,self.provider_id.ssl_pin,self.ssl_txn_id)
        print("Requiest",payload)
        result = requests.post(url, data={'xmldata': payload}, headers=headers)
        print("555",(result.text))
        xml_json = xmltodict.parse(result.content)
        res_json=json.dumps(xml_json)
        response = json.loads(res_json)
        response=response['txn']
        print(" Delete response",response)
        success_code = response.get('ssl_result_message')
        ssl_transaction_type=response.get('ssl_transaction_type')
        print("success_code",success_code, ssl_transaction_type)
        if not success_code:
            raise ValidationError("Elavon_Pay: " + _("Received data with missing success code."))
        elif success_code =="APPROVAL" and ssl_transaction_type =='DELETE':
            print("DELETE")
            self._set_delete_state()            
        else:
            _logger.warning(
                "Received data with invalid success code (%s) for transaction with primary response "
                "code %s and reference %s.", success_code, primary_response_code, self.reference
            )
            self._set_error("Elavon_Pay: " + _("Unknown success code: %s", success_code))



     # {'ssl_amount': '23.00', 'ssl_card_short_description': 'MC', 'ssl_get_token': 'Y', 
     # 'ssl_token_response': 'SUCCESS', 'ssl_token': '5470052779992124', 'ssl_last_name': 'gupta',
     #  'ssl_approval_code': '773351', 'ssl_email': 'v@gmail.com', 'ssl_exp_date': '1234', 
     #  'ssl_first_name': 'vimal', 'ssl_invoice_number': 'S00049-20240726192619', 
     #  'ssl_txn_id': '260724O2C-8C8FCBBF-097E-45CA-A6C9-9FF517750CF8', 'ssl_transaction_type': 'SALE', 
     #  'ssl_result': '0', 'ssl_result_message': 'APPROVAL', 'ssl_card_number': '51**********2124', 'ssl_cvv2_response': 'M', 
     #  'ssl_txn_time': '07/26/2024 03:26:33 PM'}


    def _elavon_tokenize_from_notification_data(self, notification_data):
        print("_elavon_tokenize_from_notification_data",notification_data)
        """ Create a new token based on the notification data.

        :param dict notification_data: The notification data built with Stripe objects.
                                       See `_process_notification_data`.
        :return: None
        """
        # payment_method = notification_data.get('payment_method')
        # if not payment_method:
        #     _logger.warning(
        #         "requested tokenization from notification data with missing payment method"
        #     )
        #     return

        # # Extract the Stripe objects from the notification data.
        # if self.operation == 'online_direct':
        #     customer_id = notification_data['payment_intent']['customer']
        # else:  # 'validation'
        #     customer_id = notification_data['setup_intent']['customer']
        # # Another payment method (e.g., SEPA) might have been generated.
        # if not payment_method[payment_method['type']]:
        #     payment_methods = self.provider_id._stripe_make_request(
        #         f'customers/{customer_id}/payment_methods', method='GET'
        #     )
        #     _logger.info("Received payment_methods response:\n%s", pprint.pformat(payment_methods))
        #     payment_method = payment_methods['data'][0]

        # Create the token.
        token = self.env['payment.token'].create({
            'provider_id': self.provider_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_details': notification_data.get('ssl_card_number'),
            'partner_id': self.partner_id.id,
            'provider_ref': notification_data.get('ssl_token'),
            #'elavon_payment_method': payment_method['id'],
            'elavon_mandate': notification_data.get('ssl_token'),
        })
        print("tokentoken",token)
        self.write({
            'token_id': token,
            'tokenize': False,
        })
        _logger.info(
            "created token with id %(token_id)s for partner with id %(partner_id)s from "
            "transaction with reference %(ref)s",
            {
                'token_id': token.id,
                'partner_id': self.partner_id.id,
                'ref': self.reference,
            },
        )
    def _payment_by_token(self,processing_values):
        url = const.API_URLS['process_live']['live'] if self.provider_id.state =='enabled'  else const.API_URLS['process_test']['test']#"https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
        payload='''
        xmldata=
          "<txn>
            <ssl_transaction_type>ccsale</ssl_transaction_type>
            <ssl_account_id>{}</ssl_account_id>
            <ssl_user_id>{}</ssl_user_id>
            <ssl_pin>{}</ssl_pin>
            <ssl_amount>{}</ssl_amount>           
            <ssl_invoice_number>{}</ssl_invoice_number>
            <ssl_token>{}</ssl_token>
            <ssl_merchant_initiated_unscheduled>Y</ssl_merchant_initiated_unscheduled>
           
          </txn>"

        '''
        print("processing_values", processing_values, self.token_id ,processing_values.get('reference')[11:])
        provider_id=self.env['payment.provider'].search([('id','=',processing_values.get('provider_id'))])
        #token_id=self.env['payment.token'].search([('id', '=',processing_values.get('partner_id'))])
        print("provider_id token",provider_id,self.token_id, self.provider_id.ssl_merchant_id,self.provider_id.ssl_user_id,self.provider_id.ssl_pin, processing_values.get('amount'),processing_values.get('reference'),self.token_id.elavon_mandate)
        payload=payload.format(self.provider_id.ssl_merchant_id,self.provider_id.ssl_user_id,self.provider_id.ssl_pin, processing_values.get('amount'),processing_values.get('reference')[11:],self.token_id.elavon_mandate )
        7888
        print("payloadpayload",payload)
        headers = {
              'Content-Type': 'application/x-www-form-urlencoded'
            }

        response = requests.post(url, data={'xmldata': payload}, headers=headers)

        print("5555678987678987656789876567898765678",type(response.text))
        xml_json = xmltodict.parse(response.content)
        res_json=json.dumps(xml_json)
        response = json.loads(res_json)
        response=response['txn']

        #print("res",response['txn'])

        return response

    def _get_processing_values(self):
        """ Return the values used to process the transaction.

        The values are returned as a dict containing entries with the following keys:

        - `provider_id`: The provider handling the transaction, as a `payment.provider` id.
        - `provider_code`: The code of the provider.
        - `reference`: The reference of the transaction.
        - `amount`: The rounded amount of the transaction.
        - `currency_id`: The currency of the transaction, as a `res.currency` id.
        - `partner_id`: The partner making the transaction, as a `res.partner` id.
        - Additional provider-specific entries.

        Note: `self.ensure_one()`

        :return: The processing values.
        :rtype: dict
        """
        self.ensure_one()
        processing_values =super()._get_processing_values()
        if self.token_id:        
            print(" token ttttt_get_processing_values",processing_values)
            response=self._payment_by_token(processing_values)
            tx=self._process_notification_data(response)
        

        return processing_values

    def _get_specific_processing_values(self, processing_values):
        """ Override of payment to return an access token as provider-specific processing values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'elavon':
            return res

        return {
            'access_token': payment_utils.generate_access_token(
                processing_values['reference'], processing_values['partner_id']
            )
        }


    def action_recurring(self, ssl_billing_cycle,ssl_end_of_month,ssl_next_payment_date):
        print("action_recurring transactions",ssl_billing_cycle,ssl_end_of_month,ssl_next_payment_date)
        if ssl_billing_cycle and ssl_end_of_month and ssl_next_payment_date:
            self.ensure_one()

          
            url = const.API_URLS['process_live']['live'] if self.provider_id.state =='enabled'  else const.API_URLS['process_test']['test']#"https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
            payload = '''
                    <txn>
                      <ssl_merchant_id>{}</ssl_merchant_id>
                      <ssl_user_id>{}</ssl_user_id>
                      <ssl_pin>{}</ssl_pin>
                      <ssl_transaction_type>ccaddrecurring</ssl_transaction_type>
                      <ssl_txn_id>{}</ssl_txn_id>
                      <ssl_billing_cycle>{}</ssl_billing_cycle>
                      <ssl_next_payment_date>{}</ssl_next_payment_date>
                      <ssl_amount>{}</ssl_amount>
                      <ssl_end_of_month>{}</ssl_end_of_month>
                      
                    </txn>
                    '''
            headers = {
                  'Content-Type': 'application/x-www-form-urlencoded'
                }
            payload=payload.format(self.provider_id.ssl_merchant_id,self.provider_id.ssl_user_id,self.provider_id.ssl_pin,self.ssl_txn_id,ssl_billing_cycle,ssl_next_payment_date.strftime("%m/%d/%Y"), self.amount,ssl_end_of_month)
            print("Requiest",payload)
            result = requests.post(url, data={'xmldata': payload}, headers=headers)
            print("555",(result.text))
            xml_json = xmltodict.parse(result.content)
            res_json=json.dumps(xml_json)
            response = json.loads(res_json)
            response=response['txn']
            print(" Recurring response",response)
            self.recurring_active=True

        else:
            return False




    def elavon_make_installment(self,amount,ssl_billing_cycle,ssl_next_payment_date,ssl_end_of_month,ssl_total_installments):
        print("elavon_make_installment transaction")
        self.ensure_one()
        if amount and ssl_billing_cycle and ssl_next_payment_date and ssl_end_of_month and ssl_total_installments:
            url = const.API_URLS['process_live']['live'] if self.provider_id.state =='enabled'  else const.API_URLS['process_test']['test']#"https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
            transaction_id=self.env['payment.transaction'].search([('id','=', self.env.context.get('active_id'))], limit=1)
            payload = '''
                    <txn>
                      <ssl_transaction_type>ccaddinstall</ssl_transaction_type>
                      <ssl_merchant_id>{}</ssl_merchant_id>
                      <ssl_user_id>{}</ssl_user_id>
                      <ssl_pin>{}</ssl_pin>                 
                      <ssl_txn_id>{}</ssl_txn_id>
                      <ssl_amount>{}</ssl_amount>
                      <ssl_next_payment_date>{}</ssl_next_payment_date>
                      <ssl_billing_cycle>{}</ssl_billing_cycle>
                      <ssl_end_of_month>{}</ssl_end_of_month>
                      <ssl_total_installments>{}</ssl_total_installments>

                     

                    </txn>
                    '''
            headers = {
                  'Content-Type': 'application/x-www-form-urlencoded'
                }
            payload=payload.format(self.provider_id.ssl_merchant_id,self.provider_id.ssl_user_id,self.provider_id.ssl_pin,self.ssl_txn_id, amount,ssl_next_payment_date.strftime("%m/%d/%Y"),ssl_billing_cycle,ssl_end_of_month,ssl_total_installments)
            print("Requiest",payload)
            result = requests.post(url, data={'xmldata': payload}, headers=headers)
            print("555",type(result.text))
            xml_json = xmltodict.parse(result.content)
            res_json=json.dumps(xml_json)
            response = json.loads(res_json)
            response=response['txn']
            self.installment_active=True
        
            return response

        else:

            return {'Error':"Some data missing"}


