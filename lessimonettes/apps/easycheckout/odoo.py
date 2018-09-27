import odoorpc
import datetime
from django.conf import settings

def odoo_connect():
    odoo = odoorpc.ODOO(settings.ODOO_SERVER, protocol='jsonrpc+ssl', port=443)
    odoo.login(settings.ODOO_DATABASE, settings.ODOO_LOGIN, settings.ODOO_PASSWORD)
    return odoo

def get_partner(odoo, order):
    #Get or create partner
    partner_ids = odoo.execute('res.partner', 'search', [('email', '=', order.user.email)])
    partner = partner_ids
    if not partner_ids:
        new_partner_ids = odoo.execute('res.partner', 'create', {'name': order.shipping_address.name, 'phone': order.shipping_address.phone, 'street': order.shipping_address.address1, 'street2': order.shipping_address.address2, 'zip': order.shipping_address.zip_code, 'city': order.shipping_address.city, 'email': order.user.email })
        partner = new_partner_ids
    return partner[0]

def create_order_sale(odoo, order, partner, odoo_codes):
    order_reference = "SO"+str(int(get_last_order(odoo))+1) 
    #{@reference_code}_#{@customer_odoo_id}"
    values = {
        'currency_id': 1,
        #'date_order': '',
        'name': order_reference,
        'payment_term': 1,
        'partner_id': partner
    }
    order_id = odoo.execute('sale.order', 'create', values)
    for p in odoo_codes:
        print(str(p))
        product_id = odoo.execute('product.product', 'search', [('default_code', '=', str(p[0]))])
        print(str(product_id[0]))
        line_values =  {'product_id': product_id[0],
                        'product_uom_qty': int(p[1]),
                    'order_id': order_id}
        sale_order_line = odoo.execute('sale.order.line', 'create', line_values)
    if int(order.get_delivery()) > 1:
        product_id = odoo.execute('product.product', 'search', [('default_code', '=', 'PATR01')])
        line_values =  {'product_id': product_id[0],
                        'product_uom_qty': 1,
                        'price_unit': float(order.get_delivery())/1.20,
                    'order_id': order_id}
        sale_order_line = odoo.execute('sale.order.line', 'create', line_values)
    
    return order_id

def get_last_order(odoo):
    if 'sale.order' in odoo.env:
        Order = odoo.env['sale.order']
        order_ids = Order.search([])
        orders = []
        for order in Order.browse(order_ids):
            name = order.name
            if 'SO' in name:
                name = name.replace('SO', '')
                orders.append(int(name))
        orders.sort()
        last_order_id = orders[-1]
        return last_order_id

