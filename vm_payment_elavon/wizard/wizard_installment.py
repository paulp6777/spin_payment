# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
import xmltodict, json
from datetime import datetime


class WizardInstallmentPayment(models.TransientModel):
    _name = 'wizard.installment.payment'
    _description = 'installment Payment'


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        print("default_get",self.env.context)
        if self.env.context.get('active_id'):
            transaction_id=self.env['payment.transaction'].search([('id','=', self.env.context.get('active_id'))], limit=1)
            res['amount']=transaction_id.amount
            res['ssl_next_payment_date']=transaction_id.ssl_next_payment_date
            res['ssl_total_installments']=transaction_id.ssl_total_installments

        return res


    amount=fields.Float('Installment Amount')  
    ssl_billing_cycle=fields.Selection([('DAILY','DAILY'),('BIWEEKLY','BIWEEKLY'),('SEMIMONTHLY','SEMIMONTHLY'),
                    ('MONTHLY','MONTHLY'),('BIMONTHLY','BIMONTHLY'),('QUARTERLY','QUARTERLY'),('SEMESTER','SEMESTER'),
                    ('SUSPENDED','SUSPENDED')], string="Billing Cycle")

    ssl_next_payment_date=fields.Date('Next Payment Date')
    ssl_end_of_month=fields.Selection([('Y','Y'),('N','N')],string="EOD of Month", default='N')
    ssl_total_installments=fields.Selection([('3','3'),('4','4'),('5','5'), ('6','6'),('7','7'),('8','8'),('9','9'), ('10','10'),('11','11'),('12','12')], string="Total Installment")
    # ssl_total_installments=fields.Integer('Total Installment')


    def elavon_make_installment(self):
        print("elavon_make_installment")
        self.ensure_one()
        transaction_id=self.env['payment.transaction'].search([('id','=', self.env.context.get('active_id'))], limit=1)
        no_of_installment=int(self.ssl_total_installments)
        transaction_id.elavon_make_installment(round((self.amount/no_of_installment),2),self.ssl_next_payment_date,self.ssl_billing_cycle,self.ssl_end_of_month,self.ssl_total_installments)
        # url = "https://api.demo.convergepay.com/VirtualMerchantDemo/processxml.do"
        # transaction_id=self.env['payment.transaction'].search([('id','=', self.env.context.get('active_id'))], limit=1)
        # payload = '''
        #         <txn>
        #           <ssl_transaction_type>ccaddinstall</ssl_transaction_type>
        #           <ssl_merchant_id>{}</ssl_merchant_id>
        #           <ssl_user_id>{}</ssl_user_id>
        #           <ssl_pin>{}</ssl_pin>                 
        #           <ssl_txn_id>{}</ssl_txn_id>
        #           <ssl_amount>{}</ssl_amount>
        #           <ssl_next_payment_date>08/25/2024</ssl_next_payment_date>
        #           <ssl_billing_cycle>{}</ssl_billing_cycle>
        #           <ssl_end_of_month>{}</ssl_end_of_month>
        #           <ssl_total_installments>{}</ssl_total_installments>

                 

        #         </txn>
        #         '''
        # headers = {
        #       'Content-Type': 'application/x-www-form-urlencoded'
        #     }
        # payload=payload.format(transaction_id.provider_id.ssl_merchant_id,transaction_id.provider_id.ssl_user_id,transaction_id.provider_id.ssl_pin,transaction_id.ssl_txn_id, self.amount,self.ssl_billing_cycle,self.ssl_end_of_month,self.ssl_total_installments)
        # print("Requiest",payload)
        # 0000
        # result = requests.post(url, data={'xmldata': payload}, headers=headers)
        # print("555",type(result.text))
        # xml_json = xmltodict.parse(result.content)
        # res_json=json.dumps(xml_json)
        # response = json.loads(res_json)
        # response=response['txn']
        
        # return response



