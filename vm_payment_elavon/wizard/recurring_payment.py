# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
import xmltodict, json
from datetime import datetime


class RecurringMakePayment(models.TransientModel):
    _name = 'elavon.recurring.payment'
    _description = 'elavon.recurring.payment'


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        print("default_get",self.env.context)
        if self.env.context.get('active_id'):
        	#move_id=self.env['account.move'].search([('id','=',self.env.context.get('active_id'))])
        	transaction_id=self.env['payment.transaction'].search([('id','=',self.env.context.get('active_id'))])
        	#print("transaction_id",transaction_id,move_id)
        	res['transaction_id']=transaction_id.id
        	res['ssl_amount']=transaction_id.amount
        	res['ssl_next_payment_date']=transaction_id.ssl_next_payment_date
        	res['ssl_billing_cycle']=transaction_id.ssl_billing_cycle

        return res

    ssl_next_payment_date=fields.Date('Next Payment Date')
    ssl_end_of_month=fields.Selection([('Y','Y'),('N','N')], string="End Of Month", default='N')
    ssl_billing_cycle=fields.Selection([('MONTHLY','MONTHLY'),('QUARTERLY','QUARTERLY'),('ANNUALLY','ANNUALLY')],string="Biiling Cycle", default='MONTHLY')
    ssl_amount=fields.Float('Recurring Amount')
    transaction_id=fields.Many2one('payment.transaction', 'Transaction NO.')


# <txn>
#     <ssl_merchant_id>my_merchant_id</ssl_merchant_id>
#     <ssl_user_id>my_user_id</ssl_user_id>
#     <ssl_pin>my_pin</ssl_pin>
#     <ssl_test_mode>False</ssl_test_mode>
#     <ssl_transaction_type>ccaddrecurring</ssl_transaction_type>
#     <ssl_card_number>00**********0000</ssl_card_number>
#     <ssl_exp_date>1230</ssl_exp_date>
#     <ssl_amount>10.36</ssl_amount>
#     <ssl_billing_cycle>MONTHLY</ssl_billing_cycle>
#     <ssl_next_payment_date>01/31/2022</ssl_next_payment_date>
#     <ssl_end_of_month>Y</ssl_end_of_month>25/08/2024-08-25
#     <ssl_invoice_number>1111</ssl_invoice_number>

# </txn>

    def action_recurring(self):
        print("action_recurring")
        self.ensure_one()
        self.transaction_id.action_recurring(self.ssl_billing_cycle,self.ssl_end_of_month, self.ssl_next_payment_date)

        # url = "https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
        # payload = '''
        #         <txn>
        #           <ssl_merchant_id>{}</ssl_merchant_id>
        #           <ssl_user_id>{}</ssl_user_id>
        #           <ssl_pin>{}</ssl_pin>
        #           <ssl_transaction_type>ccaddrecurring</ssl_transaction_type>
        #           <ssl_txn_id>{}</ssl_txn_id>
        #           <ssl_billing_cycle>DAILY</ssl_billing_cycle>
        #           <ssl_next_payment_date>07/28/2024</ssl_next_payment_date>
        #           <ssl_amount>{}</ssl_amount>
        #           <ssl_end_of_month>{}</ssl_end_of_month>
                  
        #         </txn>
        #         '''
        # headers = {
        #       'Content-Type': 'application/x-www-form-urlencoded'
        #     }
        # payload=payload.format(self.transaction_id.provider_id.ssl_merchant_id,self.transaction_id.provider_id.ssl_user_id,self.transaction_id.provider_id.ssl_pin,self.transaction_id.ssl_txn_id, self.ssl_amount,self.ssl_end_of_month)
        # print("Requiest",payload)
        # result = requests.post(url, data={'xmldata': payload}, headers=headers)
        # print("555",(result.text))
        # xml_json = xmltodict.parse(result.content)
        # res_json=json.dumps(xml_json)
        # response = json.loads(res_json)
        # response=response['txn']
        # print(" Recurring response",response)



