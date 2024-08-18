# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    elavon_payment_method = fields.Char(string="Elavon Payment Method ID", readonly=True)
    elavon_mandate = fields.Char(string="Elavon Mandate", readonly=True)


