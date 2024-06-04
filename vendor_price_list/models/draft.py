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

# لو اليوزر اشترى من فينتور بالسعر  معين هيسجل

#  record vendor line with his price and his date create po  in product.templite in tap purchase
# how can if user create po with same vendor and same product but another price
# why it  this price not recorded  in  in product.templite in tap purchase  and his date create po


# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'

#     @api.model
#     def create(self, values):
#         order = super(PurchaseOrder, self).create(values)
#         order.update_supplier_info()
#         return order

#     def write(self, values):
#         res = super(PurchaseOrder, self).write(values)
#         self.update_supplier_info()
#         return res

#     def update_supplier_info(self):
#         for order in self:
#             # Create a set to store unique product template IDs with different prices
#             product_templates = set()

#             # Iterate over each order line to find lines with different prices
#             for line in order.order_line:
#                 # Search for the last supplier information record for this product template
#                 supplier_info = self.env['product.supplierinfo'].search([
#                     ('partner_id', '=', order.partner_id.id),
#                     ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
#                 ], order='id desc', limit=1)
#                 purchases = self.env['purchase.order'].search([
#                     ('state', 'in', ('purchase', 'done')),
#                     ('order_line.product_id', 'in',
#                      self.product_tmpl_id.product_variant_ids.ids),
#                     ('partner_id', 'in', self.partner_id.ids),
#                 ], order='date_order')

#                 # Check if the supplier_info exists and if the price is different
#                 if supplier_info and supplier_info.price != line.price_unit:
#                     print(" new line.price_unit ", line.price_unit,)
#                     print("  supplier_info.write  supplier_info.price supplier_info.last_purchase_date",
#                           supplier_info.id, supplier_info.price, supplier_info.last_purchase_date)
#                     # If the price is different, add the product template ID to the set
#                     product_templates.add(line.product_id.product_tmpl_id.id)

#             # Create a new supplier info record for each unique product template with a different price
#             for product_template_id in product_templates:
#                 print(" no supplier line.price_unit ", line.price_unit,)

#                 self.env['product.supplierinfo'].create({
#                     'partner_id': order.partner_id.id,
#                     'product_tmpl_id': product_template_id,
#                     'price': line.price_unit,
#                     # Set other fields as needed
#                 })

# Create a new record only if conditions are met

# def update_supplier_info(self):
#     for order in self:
#         for line in order.order_line:
#             supplier_info = self.env['product.supplierinfo'].search([
#                 ('partner_id', '=', order.partner_id.id),
#                 ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),
#                 ('price', '!=', line.price_unit),

#             ], limit=1)

#             # Check if the supplier_info exists and if the price is different
#             if supplier_info and supplier_info.price != line.price_unit:
#                 print(" new line.price_unit ", line.price_unit,)
#                 print("  supplier_info.write  price_unit",
#                       supplier_info, supplier_info.price)
#                 self.env['product.supplierinfo'].create({
#                     'partner_id': order.partner_id.id,
#                     'product_tmpl_id': line.product_id.product_tmpl_id.id,
#                     'price': line.price_unit,
#                     # Set other fields as needed
#                 })

# if supplier_info:
#     print(" new line.price_unit ", line.price_unit,)
#     print("  supplier_info.write  price_unit",
#           supplier_info, supplier_info.price)
#     # supplier_info.write({
#     #     'price': line.price_unit,
#     #     # Update other fields as needed
#     # })
# else:
#     print(" no supplier line.price_unit ", line.price_unit,)
#     self.env['product.supplierinfo'].create({
#         'partner_id': order.partner_id.id,
#         'product_tmpl_id': line.product_id.product_tmpl_id.id,
#         'price': line.price_unit,
#         # Set other fields as needed
#     })


class Productsupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    product_template_id = fields.Many2one(
        'product.template', string='Product Name', store=True)
    product_name = fields.Char(
        compute='_compute_product_name', string='Product Name', store=True)
    # purchase_order_ids = fields.Many2many(
    #     'purchase.order', string='Purchase Orders', compute='_compute_purchase_order_ids', store=True)
    purchase_order_ids = fields.Integer(
        string='Purchase Orders ids', store=True)

    # @api.depends('product_template_id', 'partner_id')
    # def _compute_purchase_order_ids(self):
    #     for supplier in self:
    #         purchases = self.env['purchase.order'].search([
    #             ('state', 'in', ('purchase', 'done')),
    #             ('order_line.product_id.product_tmpl_id',
    #              '=', supplier.product_template_id.id),
    #             ('partner_id', '=', supplier.partner_id.id),
    #         ])
    #         supplier.purchase_order_ids = [(6, 0, purchases.ids)]
    #         print('purchase_order_ids product_name',
    #               supplier.purchase_order_ids)

    @api.model
    def _compute_product_name(self):
        for record in self:

            print(' Self product_name',  record.product_name)

    last_purchase_date = fields.Date(
        'Last Purchase', compute='_compute_last_purchase_date')

    @api.model
    def _compute_last_purchase_date(self):

        self.last_purchase_date = False
        purchases = self.env['purchase.order'].search([
            ('state', 'in', ('purchase', 'done')),
            ('order_line.product_id', 'in',
             self.product_tmpl_id.product_variant_ids.ids),
            ('partner_id', 'in', self.partner_id.ids),
        ], order='date_order')
        for supplier in self:

            products = supplier.product_tmpl_id.product_variant_ids
            for purchase in purchases:
                supplier.product_name = purchase.order_line.product_id.name
                supplier.last_purchase_date_with_update_price = purchase.order_line.date_order
                # supplier.purchase_order_ids = purchase.order_line.id
                print("Product Name:  and supplier.product_template_id  supplier.last_purchase_date_with_update_price ", supplier.last_purchase_date_with_update_price,
                      supplier.product_name, supplier.product_template_id, ' purchase.order_line.id ', supplier.purchase_order_ids)
                if purchase.partner_id != supplier.partner_id:
                    continue
                if not (products & purchase.order_line.product_id):
                    continue
                supplier.last_purchase_date = purchase.date_order
                break

    last_purchase_date_with_update_price = fields.Date(
        'Last Purchase with Updated Price')

    @api.model
    def _default_last_purchase_date_with_update_price(self):
        return self.last_purchase_date

    @api.model
    def create(self, vals):
        if 'last_purchase_date_with_update_price' not in vals:
            last_purchase_date = vals.get(
                'last_purchase_date', self.last_purchase_date)
            vals['last_purchase_date_with_update_price'] = last_purchase_date
            print('last_purchase_date_with_update_price not in vals')

        print('last_purchase_date_with_update_price  in vals',
              vals['last_purchase_date_with_update_price'])
        return super(Productsupplierinfo, self).create(vals)

    # @api.depends('price')
    # def _compute_last_purchase_date(self):
    #     for record in self:
    #         if record.price:
    #             record.last_purchase_date = fields.Date.today()
    #             print('Date.today()', record.last_purchase_date)


class VendorLine(models.Model):
    _name = 'product.template.vendor.line'
    _description = 'Vendor Line'

    vendor_id = fields.Many2one('res.partner', string='Vendor')
    last_purchase_date = fields.Date(string='Last Purchase Date')
    last_price = fields.Float(string='Last Price')
    product_template_id = fields.Many2one(
        'product.template', string='Product Template')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vendor_product_line_ids = fields.One2many(
        'product.template.vendor.line', 'product_template_id', string='Vendor Lines')
