
from odoo import http
from odoo.http import request




class WebsiteSaleDelivery(http.Controller):
    
    @http.route('/elavon/installment_option', type='json', auth='public', website=True)
    def installment_options(self,  **post):
    	print("installment_option",post, post.get('installment_option'))
    	order = request.website.sale_get_order().sudo()
    	print("order",order)
    	if order:
    		order.write({
                'installment_option':post.get('installment_option') if post.get('installment_option') else False
              
            })
    		return {'status': 'success'}
    		return {'status': 'error'}

    @http.route('/elavon/ssl_total_installments', type='json', auth='public', website=True)
    def total_installments(self,  **post):
    	print("ssl_total_installments",post, post.get('ssl_total_installments'))
    	order = request.website.sale_get_order().sudo()
    	print("order",order)
    	if order:
    		order.write({
                'ssl_total_installments':post.get('ssl_total_installments') if post.get('ssl_total_installments') else False
              
            })
    		return {'status': 'success'}
    		return {'status': 'error'}


    @http.route('/elavon/ssl_billing_cycle', type='json', auth='public', website=True)
    def billing_option(self,  **post):
    	print("billing_option",post, post.get('ssl_billing_cycle'))
    	order = request.website.sale_get_order().sudo()
    	print("order",order)
    	if order:
    		order.write({
                'ssl_billing_cycle':  post.get('ssl_billing_cycle'),
              
            })
    		return {'status': 'success'}
    		return {'status': 'error'}

    @http.route('/elavon/recurring', type='json', auth='public', website=True)
    def recurring_option(self,  **post):
    	print("recurring_option",post, post.get('recurring'))
    	order = request.website.sale_get_order().sudo()
    	print("orecurring_option order",order)
    	if order:
    		order.write({
                           'recurring':post.get('recurring') if post.get('recurring') else False
              
            })
    		return {'status': 'success'}
    		return {'status': 'error'}
       

# class MyPaymentController(http.Controller):

#     @http.route(['/shop/payment'], type='http', auth="public", website=True)
#     def payment_transaction(self, **post):
#         installment_option = post.get('installment_option')
#         order = request.website.sale_get_order()

#         if order:
#             order.installment_option = installment_option

#         return request.redirect('/shop/confirmation')