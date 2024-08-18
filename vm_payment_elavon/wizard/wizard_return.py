# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
import xmltodict, json
from datetime import datetime


class WizardReturnPayment(models.TransientModel):
    _name = 'wizard.return.payment'
    _description = 'Return Payment'


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        print("default_get",self.env.context)
        if self.env.context.get('active_id'):
            transaction_id=self.env['payment.transaction'].search([('id','=', self.env.context.get('active_id'))], limit=1)
            res['amount']=transaction_id.amount

        return res  


    amount=fields.Float('Amount')

    def action_refund(self):
        if self.env.context.get('active_id'):
            transaction_id=self.env['payment.transaction'].search([('id','=', self.env.context.get('active_id'))], limit=1)

            if transaction_id.amount < self.amount:
                raise UserError("Amount should be not greater then transaction amount.")

            else:
                transaction_id.action_refund(self.amount)






