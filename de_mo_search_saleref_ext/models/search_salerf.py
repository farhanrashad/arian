# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, modules,fields, _

class UsersExt(models.Model):
    _inherit = 'stock.picking'
