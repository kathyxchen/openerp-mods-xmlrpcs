from openerp.osv import fields, osv
from openerp import pooler
# this one is to help with a default option below
import time
import decimal_precision as dp

class product_product(osv.osv):
    _name='product.product'
    _inherit='product.product'
    _columns={
        'footprint': fields.char('Footprint', size=100, ondelete='set null'),
        'manu_name': fields.char('Manufacturer', size=100, ondelete='set null'),
        'stock_notes': fields.text('Notes'),
    }

product_product()