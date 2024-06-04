from datetime import datetime
from odoo import models, api
from odoo import fields, models, api, _
from odoo import http
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError  # Import UserError
from odoo.http import request
# /shop/pro
import logging

_logger = logging.getLogger(__name__)


class Productsupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    product_template_id = fields.Many2one(
        'product.template', string='Product Name', store=True)
    product_name_of_partner = fields.Char(
        compute='_compute_product_name', string='Product Name', store=True)
    # purchase_order_ids = fields.Many2many(
    #     'purchase.order', string='Purchase Orders', compute='_compute_purchase_order_ids', store=True)
    purchase_order_ids = fields.Integer(
        string='Purchase Orders ids', store=True)

    @api.depends('product_name_of_partner', 'price', 'last_purchase_date_with_update_price')
    def _compute_product_name(self):
        for record in self:
            record.product_name_of_partner = record.product_tmpl_id.name

    last_purchase_date_with_update_price = fields.Date(
        'Last Purchase with Updated Price')
