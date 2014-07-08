# This python script essentially just creates the tables for you.
# If you wanted to calculate a new field based on
# other fields that you have inputted manually, you could just create a function to enter in the data automatically. 
# this would be the fields.function type

# always need to import these for data to be loaded into tables properly
from openerp.osv import fields, osv
from openerp import pooler

# format is pretty much the same for all of these: each class is going to end up being a table in the SQL database
class res_partner(osv.osv):
    _description='partner'
    _inherit='res.partner' # this one inherits the "res.partner" module, which is Partner on the web client
    _name='res.partner'
    _columns={ # essentially just adding one more field to it. 
        # note that this field is of type "one2many", meaning this is 'one' field that is associated with many pieces of data--
        # the 'many' is pretty much another table
        'payment_id': fields.one2many('res.partner.payarch', 'partner_id', 'Customer Payment Archive'),
    }

res_partner()

# here's the 'many' table:
class res_partner_payarch(osv.osv): # no inheritance this time, this is a standalone table that just happens to be linked to Partner now.
    _name='res.partner.payarch'
    _description='payment archive'
    # you can order the information inputted based on your fields
    _order='date_rec desc, balance desc, inv_date desc'
    _columns={
        'date_rec': fields.date('Date Received'),
        'po_num': fields.char('PO #', size=200), # 200 charac. limit
        'invoice': fields.char('Invoice #', size=200),
        'inv_date' : fields.date('Invoice Date'),
        'mo_date' : fields.date('M/O Date'),
        'description': fields.char('Description', size=1000),
        'balance': fields.integer('Balance ($)'),
        # every one2many field needs a many2one field to link the two together! we never need to fill this out on our form
        # but the row in the table is automatically associated with the partner you just added it in. 
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade'),
    }

res_partner_payarch()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

