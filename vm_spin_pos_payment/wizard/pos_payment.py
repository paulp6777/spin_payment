# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
import xmltodict, json
from datetime import datetime


class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'
    _description = 'Point of Sale Make Payment Wizard'


    # def _default_auth_payment(self):
    #     active_id = self.env.context.get('active_id')
    #     if self.payment_method_id.spin_pos_terminal_id.transtypes =='Auth':
    #         return True
    #     return False


    transtype=fields.Selection([('Return','Return'),('Void', 'Void')],default='Return')
    is_auth_payment=fields.Boolean("Is Auth")

   
    @api.onchange('payment_method_id')
    def _onchange_auth_payment(self):
    	if self.payment_method_id:
    		print("self.payment_method_id.spin_pos_terminal_id.transtypes")
    		if self.payment_method_id.spin_pos_terminal_id.transtypes =='Auth':
    			print("self.payment_method_id.spin_pos_terminal_id.transtypes333333333333333")
    			self.is_auth_payment=True
    			print("self.is_auth_payment",self.is_auth_payment)

    		else:
    			self.is_auth_payment=False
    	else:

    			self.is_auth_payment=False




    def check(self):
    	order = self.env['pos.order'].browse(self.env.context.get('active_id', False))


    	print("orderorderorder",order.refunded_order_ids, self.payment_method_id.use_payment_terminal)
    	#spin_payment_obj=Void
    	if self.payment_method_id.use_payment_terminal =='spin':
    		teminal_id= self.payment_method_id.spin_pos_terminal_id
    		if teminal_id:
    			if teminal_id.terminal_status() == True:
    				print("orderorder date",order.refunded_order_ids[0].date_order, int(datetime.strftime(order.refunded_order_ids[0].date_order , "%H")) ,int(teminal_id.void_time))
    				
    				TransType=""
    				if self.payment_method_id.spin_pos_terminal_id.transtypes =='Auth':
    					print("TransType",self.transtype)
    					TransType=self.transtype
    				else:
	    				if int(datetime.strftime(order.refunded_order_ids[0].date_order , "%H")) < int(teminal_id.void_time):
	    					TransType ="Return"

	    				else:
	    					TransType="Void"
	    			order_name=order.refunded_order_ids[0].pos_reference
	    			print("orderorder",order)	    			

    				order_name= order_name.lstrip('Order ')
    				amount=self.amount
    				if amount <0:
    					amount=-(amount)
    				else:
    					amount=amount

    				return_url=(teminal_id.terminal_ip_address+"/cgi.html?TerminalTransaction=<request><PaymentType>Credit</PaymentType><TransType>%s</TransType><Amount>%s</Amount><Tip>0.00</Tip><Frequency>OneTime</Frequency><InvNum></InvNum><RefId>%s</RefId><RegisterId>%s</RegisterId><AuthKey>%s</AuthKey><PrintReceipt>%s</PrintReceipt><SigCapture>%s</SigCapture></request>" % (TransType,float(amount),order_name,teminal_id.register_id, teminal_id.auth_key, teminal_id.printreceipt, teminal_id.sigcapture))
    				print("return_urlreturn_url",return_url)
    				result=requests.get(return_url)

    				print("Result", result, result.content)
    				xml_json = xmltodict.parse(result.content)
    				res_json=json.dumps(xml_json)
    				resp = json.loads(res_json)
    				data={
						"amount":amount,
						"is_refund_payment":True


						}
    				print("resp['xmp']['response']",resp['xmp']['response'],  resp['xmp']['response']['Message'])  
    				response=resp['xmp']['response']  
    				if resp['xmp']['response']['Message'] == 'Approved':
    					var=self.env['spin.pos.terminal.payments'].create({
    						'name': response.get('RefId'),			                
			                'status':"paid" if response['Message'] == 'Approved' else 'canceled',                
			                'amount':data.get('amount'),
			                'RefId':response['RefId'],
			                'is_refund_payment':True

    					})
    					#var=self.env['spin.pos.terminal.payments']._create_spin_payment_request(resp['xmp']['response'], {**data, 'spin_terminal_id':teminal_id.id})
    					print("varvar",var)
    					payment_id=self.env['spin.pos.terminal.payments'].search([('status','=','paid'),('RefId','=',response['RefId']), ('is_refund_payment','=',True)], limit=1)
			    		print("payment_id", payment_id)

			    		if payment_id:
			    			return super().check()
			    		else:
			    			raise ValidationError(_("Payment status cancelled by terminal"))
	    					
    				else:
    					var=self.env['spin.pos.terminal.payments'].create({
    						'name': response.get('RefId'),#response.get('id'),
			                
			                'status':"paid" if response['Message'] == 'Approved' else 'canceled',                
			                'amount':data.get('amount'),
			                'RefId':response['RefId'],
			                'is_refund_payment':True

    					})
    					#rec=self.env['spin.pos.terminal.payments']._create_spin_payment_request(resp['xmp']['response'], {**data, 'spin_terminal_id':teminal_id.id})
    					print("recrecrecrec",var)
    					#return resp['xmp']['response']


		    		payment_id=self.env['spin.pos.terminal.payments'].search([('status','=','paid'),('RefId','=',order_name), ('is_refund_payment','=',True)], limit=1)
		    		print("payment_id", payment_id)

		    		if payment_id:
		    			return super().check()
		    		else:
		    			raise ValidationError(_("Payment status cancelled by terminal"))


    	else:
    		print("EEEEEEEEEEEEEEEEEEEEE")
    	
    		return super().check()
