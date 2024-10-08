# Part of Odoo. See LICENSE file for full copyright and licensing details.

from hashlib import new as hashnew

 #ssl_merchant_id: 0022742
 #ssl_user_id: apiuser
  #      ssl_pin: YA8P237WMBGE2VUNWOJXLCXKB7EL809M4W6PGUVR8O753C5GZNCBU6SAHNAB4HIR

  #invisible="module_state != 'installed'"

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.vm_payment_elavon import const


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('elavon', "Elavon")], ondelete={'elavon': 'set default'} )
    ssl_merchant_id = fields.Char( string=" Merchant ID", help="The Merchant ID solely used to identify your elavon account.", 
         required_if_provider='elavon',
        )

    ssl_user_id = fields.Char( string="Merchant User ID", help="The Merchant User ID solely used to identify your elavon account.", 
         required_if_provider='elavon',
        )

    ssl_pin = fields.Char( string="Merchant Pin", help="The Merchant Pin solely used to identify your elavon account.", 
         required_if_provider='elavon',
        )

    ssl_transaction_type=fields.Selection([('sale','Sale'),('authonly','AUTHONLY'),('ccsale','Sale'),('ccauthonly','Auth Only'),('ccreturn','Return'),('ccvoid','Void'),('cccomplete','Completion')], string="Elavon Trasnaction Type"  , required_if_provider='elavon', default="ccsale")

    recurring_active=fields.Boolean('Recurring Active')
    installment_active=fields.Boolean('Installment Active')
    partner_code=fields.Char("Partner Code", required_if_provider='elavon')

    @api.constrains('partner_code')
    def _check_partner_code(self):

        if self.partner_code != '678odoo#%@123':
             raise ValidationError(_("To activate you need an Elavon MerchantID , please contact us at 1-800-403-3297 or Support@intruxtmerchantservices.com"))

     #=== COMPUTE METHODS ===#

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'elavon').update({
            'support_manual_capture': 'partial',
            'support_refund': 'partial',
            'support_tokenization': True,
        })




    def _elavon_get_api_url(self):
        """ Return the URL of the API corresponding to the provider's state.

        :return: The API URL.
        :rtype: str
        """
        self.ensure_one()

        environment = 'production' if self.state == 'enabled' else 'test'
        api_urls = const.API_URLS[environment]['elavon']
        return api_urls


    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'elavon':
            return default_codes
        print("888888888",const.DEFAULT_PAYMENT_METHODS_CODES)
    
        return const.DEFAULT_PAYMENT_METHODS_CODES





