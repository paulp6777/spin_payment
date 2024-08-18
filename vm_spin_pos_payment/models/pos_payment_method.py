import base64

import requests
import xmltodict, json
from odoo import fields, models, api
from odoo.tools import file_open
import time
import re

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    spin_pos_terminal_id = fields.Many2one('spin.pos.terminal', string='Spin Pos Terminal')
    spin_latest_response = fields.Json('SPin History', default={})
    spin_payment_default_partner = fields.Many2one('res.partner' ,string="Spin Default partner")

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('spin', 'Spin')]

    def spin_payment_request(self, data):
        print("spin_payment_requestspin_payment_request",data)
        self.sudo().spin_latest_response = {}  # avoid handling old responses multiple times
        var=self.spin_pos_terminal_id._api_make_payment_request(data)
        print("spin_payment_requestspin_payment_request", var)
        return var

    def _is_write_forbidden(self, fields):
        whitelisted_fields = {'spin_latest_response'}
        return super(PosPaymentMethod, self)._is_write_forbidden(fields - whitelisted_fields)


    #@api.model
    def get_spin_payment_status(self, referenceId, spinUID, order):
        print("get_spin_payment_status",referenceId, spinUID, order)
        #spinUID='bcc5d3e7-0e29-4355-a480-cbefa2e070ec'

        if spinUID:
            spin_payment = self.env['spin.pos.terminal.payments'].search([('spin_uid','=',spinUID)])
            #spin_payment.pos_order_id=self.env['pos.order'].search([('pos_reference','=',order)]).id or False,

            print("Extra value",spin_payment.sudo().spin_latest_response['ExtData'])
            extra_value=spin_payment.sudo().spin_latest_response['ExtData']
            result1 = re.search('BatchNum=22,(.*)CashBack=0.00', extra_value)
            tip_amount=0.0
            if result1:
                res=result1.group(1).replace(',', '')
                print("88",res,float(res[4:]))
                tip_amount=float(res[4:])
            else:
                print("not")
            #print("TIP value",spin_payment.sudo().spin_latest_response['ExtData']['tip'])
            

            if spin_payment and spin_payment.sudo().spin_latest_response['Message'] == 'Approved':

                 return {"status": 1 ,"msg":"Approved", 'tip_amount':tip_amount}
            else:

                return {"status": 0, "msg":str(spin_payment.sudo().spin_latest_response['Message'] + str(spin_payment.sudo().spin_latest_response['HostSpecific'])), 'tip_amount':tip_amount }
        else:

            return {"status": 0, "msg":"Failed"}

