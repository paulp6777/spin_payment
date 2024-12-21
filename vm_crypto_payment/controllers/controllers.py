# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hmac
import logging
import pprint

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


_logger = logging.getLogger(__name__)


class CryptoPayController(http.Controller):  

    @http.route("/payment/crypto/success", type='http', auth='public', csrf=False, save_session=False)
    def crypto_return_from_checkout(self, **data):
        print("crypto_return_from_checkout",data)
        """ Process the notification data sent by Tap after redirection from checkout."""
        # Retrieve the tx based on the tx reference included in the return url
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'crypto', data
        )

        # Handle the notification data crafted with Peach API objects
        tx_sudo._handle_notification_data('crypto', data)
        
        #tx_sudo._set_done()
        # Redirect the user to the status page
        return request.redirect('/payment/status')
    