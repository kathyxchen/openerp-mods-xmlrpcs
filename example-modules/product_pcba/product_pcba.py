from openerp.osv import fields, osv
from openerp import pooler
# this one is to help with a default option below
import time

class product_product(osv.osv):
    _name='product.product'
    _inherit='product.product'
    def _calculate_bd_price(self, cr, uid, ids, name, args, context=None):
        res = {}
        for object in self.browse(cr, uid, ids):
            if (object.qty_board >= 0 and object.list_price >= 0):
                price = float(object.qty_board) * float(object.list_price)
                res[object.id] = price
        return res
    def _calculate_ext_price(self, cr, uid, ids, name, args, context=None):
        res = {}
        for object in self.browse(cr, uid, ids):
            if (object.list_price >= 0 and object.volume >= 0):
                price = float(object.list_price) * float(object.vol_prod)
                res[object.id] = price
        return res

    def _str_bd_price(self, cr, uid, ids, name, args, context=None):
        res = {}
        for object in self.browse(cr, uid, ids):
            if (object.qty_board >= 0 and object.list_price >= 0):
                price = float(object.qty_board) * float(object.list_price)
                res[object.id] = str(price)
        return res
    
    def _str_ext_price(self, cr, uid, ids, name, args, context=None):
        res = {}
        for object in self.browse(cr, uid, ids):
            if (object.list_price >= 0 and object.volume >= 0):
                price = float(object.list_price) * float(object.vol_prod)
                res[object.id] = str(price)
        return res

    _columns={
        'footprint': fields.char('Footprint', size=128, ondelete='set null'),
        'manu_name': fields.char('Manufacturer', size=128, ondelete='set null'),
        'qty_board': fields.integer('Quantity Per Board'),
        'qty_prod': fields.integer('Production Quantity'),
        'vol_prod': fields.integer('Volume', help="Price will be based on this volume"),
        'per_board': fields.function(_str_bd_price, string='Cost Per Board', type='char'),
        'ext_price': fields.function(_str_ext_price, string='Extended Price', type='char'),
        'deci_per_board': fields.function(_calculate_bd_price, type='float', store=True),
        'deci_ext_price': fields.function(_calculate_ext_price, type='float', store=True),
    }

product_product()