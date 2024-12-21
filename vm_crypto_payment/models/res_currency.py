# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCurrency(models.Model):
    _inherit = 'res.currency'
    _description = 'Add Currency code '



    currency_numeric_code=fields.Char('Currency Numeric Code')


