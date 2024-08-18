# Part of Odoo. See LICENSE file for full copyright and licensing details.

import hmac
import logging
import pprint

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


_logger = logging.getLogger(__name__)


class ElavonPayController(http.Controller):
    _return_url = '/payment/elavon/success'
    _webhook_url = '/payment/elavon/webhook'

    # @http.route('/payment/elavon/return',type='http', auth="public",  csrf=False)
    # def elavon_return_from_checkout(self, **data):
    #     print("elavon_return_from_checkout", data)
    #     _logger.info("handling redirection from elavon with data:\n%s", pprint.pformat(data))
    #     """ Process the notification data sent by Elavon after redirection.

    #     :param dict data: The notification data.

    #     """
    #     # Don't process the notification data as they contain no valuable information except for the
    #     # reference and Elavon doesn't expose an endpoint to fetch the data from the API.
    #     tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
    #         'elavon', data
    #     )

    #     print("tx_sudo",tx_sudo)
    #     tx_sudo._handle_notification_data('elavon', data)
    #     tx_sudo._set_done()
    #     return request.redirect('/payment/status')


    @http.route("/payment/elavon/success", type='http', auth='public', csrf=False, save_session=False)
    def elavon_return_from_checkout(self, **data):
        """ Process the notification data sent by Tap after redirection from checkout."""
        # Retrieve the tx based on the tx reference included in the return url
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'elavon', data
        )

        # Handle the notification data crafted with Peach API objects
        tx_sudo._handle_notification_data('elavon', data)
        
        #tx_sudo._set_done()
        # Redirect the user to the status page
        return request.redirect('/payment/status')
    
    @http.route("/payment/elavon/cancel", type='http', auth='public', csrf=False, save_session=False)
    def elavon_cancel_from_checkout(self, **data):
        print("elavon_cancel_from_checkout", data)
        """ Process the notification data sent by Tap after redirection from checkout."""
        # Retrieve the tx based on the tx reference included in the return url
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'elavon', data
        )

        # Handle the notification data crafted with Peach API objects
        #tx_sudo._handle_notification_data('elavon', data)
        #tx_sudo._set_canceled()
        # Redirect the user to the status page
        return request.redirect('/shop/payment')

    @http.route("/payment/elavon/recurring", type='http', auth='public', csrf=False, save_session=False)
    def elavon_recurring_from_checkout(self, **data):
        print("elavon_recurring_from_checkout",data)

        return True