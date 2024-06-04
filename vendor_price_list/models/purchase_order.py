
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def write(self, vals):
        no_updated = self.filtered(
            lambda r: r.state not in ["purchase", "done"])
        res = super().write(vals)
        if vals.get("state", "") in ["purchase", "done"]:
            no_updated.mapped("order_line").update_supplierinfo_price()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        # Iterate over each set of values to be created
        for vals in vals_list:
            partner_id = vals.get('partner_id')
            product_id = vals.get('product_id')
            price_unit = vals.get('price_unit')

            # Check if the price already exists
            existing_line = self.search([
                ('partner_id', '=', partner_id),
                ('product_id', '=', product_id),
                ('price_unit', '=', price_unit)
            ], limit=1)

            # Print a message if the price exists
            if existing_line:
                print(
                    f"Price {price_unit} already exists for partner {partner_id} and product {product_id}")

        # Create the purchase order lines
        res = super().create(vals_list)
        # Update supplier info price for the created records
        res.update_supplierinfo_price()
        return res

    def write(self, vals):
        res = super().write(vals)
        if vals.get("price_unit"):
            self.update_supplierinfo_price()
        return res

    def update_supplierinfo_price(self):
        # تصفية السطور التي ليست من نوع العرض وهي في حالة "purchase" أو "done"
        for line in self.filtered(lambda r: not r.display_type and r.order_id.state in ["purchase", "done"]):
            # البحث عن أي سطور مطابقة بغض النظر عن التاريخ
            domain = [
                ("partner_id", "=", line.partner_id.id),
                ("product_id", "=", line.product_id.id),
            ]
            # تحديث معلومات المورد دائماً

            supplier_info = self.env['product.supplierinfo'].search([
                ('partner_id', '=', line.partner_id.id),
                ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),


            ], limit=1)

            # Check if the supplier_info exists and if the price is different
            if supplier_info:
                supplier_info.last_purchase_date_with_update_price = line.order_id.date_order

            # تحديد معايير لاختيار البائع
            params = {"order_id": line.order_id}
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date(),
                uom_id=line.product_uom,
                params=params,
            )
            # إذا تم العثور على بائع، قم بتحديث معلومات المورد
            if seller:
                line._update_supplierinfo(seller)

    def _update_supplierinfo(self, seller):
        self.ensure_one()  # Ensure that only one record is being processed
        new_seller_price = self.price_unit  # Get the unit price from the current record
        # new_seller_price_date = self.date_order
        # Convert the price according to the currency if necessary
        if self.currency_id and self.currency_id != seller.currency_id:
            new_seller_price = self.currency_id._convert(
                new_seller_price,
                seller.currency_id,
                seller.company_id,
                self.date_order or fields.Date.today(),
            )

        # Convert the price according to the unit of measure (UoM) if necessary
        if self.product_uom and self.product_uom != seller.product_uom:
            new_seller_price = self.product_uom._compute_price(
                new_seller_price, seller.product_uom
            )

        # If the new price is different from the current seller price, update it
        if new_seller_price != seller.price:
            seller.sudo().price = new_seller_price
            # Update the last_purchase_date_with_update_price field
            seller.sudo().last_purchase_date_with_update_price = self.date_order  # Update the date
            # seller.sudo().product_name_of_partner = self.product_id.name  # Update the date
