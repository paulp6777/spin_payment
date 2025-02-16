# -*- coding: utf-8 -*-


from . import controllers
from . import models

from odoo.exceptions import UserError
from odoo.tools import config

from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(env):
    setup_provider(env, 'crypto')


def uninstall_hook(env):
    reset_payment_provider(env, 'crypto')

