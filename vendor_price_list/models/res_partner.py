
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ResPartner(models.Model):
    _inherit = 'res.partner'

 

    product_line_ids_purchase = fields.One2many(
        'product.supplierinfo', 'partner_id', string='Vendor Lines')
    
    
