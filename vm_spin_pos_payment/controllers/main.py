# coding: utf-8
import logging
import json
from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PosSpinController(http.Controller):

    @http.route('/pos_spin/webhook', type='http', methods=['POST'], auth='public', csrf=False)
    def webhook(self, **post):
        print("'/poo spin/webhook", post)
        if not post.get('id'):
            return
        request.env['spin.pos.terminal.payments']._spin_process_webhook(post)
        return ""
