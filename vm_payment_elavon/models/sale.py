# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ssl_billing_cycle=fields.Selection([('DAILY','DAILY'),('BIWEEKLY','BIWEEKLY'),('SEMIMONTHLY','SEMIMONTHLY'),
                    ('MONTHLY','MONTHLY'),('BIMONTHLY','BIMONTHLY'),('QUARTERLY','QUARTERLY'),('SEMESTER','SEMESTER'),
                    ('SUSPENDED','SUSPENDED')], string=" Installement Billing Cycle")
    recurring=fields.Selection([('yes','Yes'),('no','NO')],default='no')

    installment_option=fields.Selection([('yes','Yes'),('no','NO')],default='no')

    ssl_next_payment_date=fields.Date('Next Payment Date')

    ssl_total_installments=fields.Selection([('3','3'),('4','4'),('5','5'),
                    ('6','6'),('7','7'),('8','8'),('9','9'),
                    ('10','10'),('11','11'),('12','12')], string="Total Installment")