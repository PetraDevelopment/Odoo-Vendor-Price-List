{
    'name': 'Vendor Price List',
    'author':'Petra Software',
    'company': 'Petra Software',
    'maintainer': 'Petra Software',
    'website':'www.t-petra.com',
     'license': 'LGPL-3',
    'summary': 'show data of vendor in product details ,and data of product in vendor details',
    'summary': 'Odoo 15 Development',
    'depends': ['base', 'web', 'stock', 'product', 'account', 'mail', 'purchase'],
    'data': [
        'views/product_templite_inherit.xml',
        'views/res_partner_view.xml',

    ],
 'images': ['static/description/banner.png'],
     'price':15,
    'currency':'USD',

    'application': True,
}
