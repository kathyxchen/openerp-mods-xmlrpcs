from openerp.osv import fields, osv
from openerp import pooler
# this one is to help with a default option below
import time
import decimal_precision as dp 

class mrp_bom(osv.osv):
    _name='mrp.bom'
    _inherit='mrp.bom'

    def _calculate_vol(self, cr, uid, ids, name, args, context=None):
        res = {}
        for object in self.browse(cr, uid, ids):
            if (object.product_qty >= 0 and object.production >= 0):
                vol = float(object.product_qty) * float(object.production)
                res[object.id] = int(vol)
        return res
    def _calculate_bd_price(self, cr, uid, ids, name, args, context=None):
        res = {}
        for object in self.browse(cr, uid, ids):
            if (object.product_qty >= 0 and object.unit_price >= 0):
                price = float(object.product_qty) * float(object.unit_price)
                res[object.id] = price
        return res
    def _calculate_ext_price(self, cr, uid, ids, name, args, context=None):
        res = {}
        for object in self.browse(cr, uid, ids):
            if (object.unit_price >= 0 and object.vol_demanded >= 0):
                price = float(object.unit_price) * float(object.vol_demanded)
                res[object.id] = price
        return res

    _columns={
        'product_footprint': fields.related('product_id', 'footprint', type="char", store=False, readonly=True, string="Footprint"),
        'product_description': fields.related('product_id', 'description', type="char", size="128", store=False, readonly=True, string="Description"),
        'product_manu': fields.related('product_id', 'manu_name', type="char", store=False, readonly=True, string="Manufacturer"),
        'production': fields.integer('Production'),
        'unit_price': fields.float('Unit Price', digits_compute=dp.get_precision('Product Unit of Measure'), store=True),
        'vol_demanded': fields.function(_calculate_vol, string='Volume Demanded', type='integer', store=True),
        'per_board': fields.function(_calculate_bd_price, string='Cost Per Board', digits_compute=dp.get_precision('Product Unit of Measure'), type='float', store=True), 
        'ext_price':fields.function(_calculate_ext_price, string='Extended Price', digits_compute=dp.get_precision('Product Unit of Measure'), type='float', store=True),
    }
    _default={
        'code': time.strftime('%Y%m%d'),
    }

mrp_bom()