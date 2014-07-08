# always need the first two imports
from openerp.osv import fields, osv
from openerp import pooler
# this one is to help with a default option below
import time

# adds a whole new table
class quotation_file(osv.osv):
    _name='quotation.file' 
    _description='quotation module'
    # ordered by partner, date the quotation was sent/received, and quotation type 
    _order='partner_id, date_iss desc, quot_type'
    _columns={
        # partner_id links the table to my res.partner table, which has the one2many relation already (see below)
        'partner_id': fields.many2one('res.partner', 'Partner Name', ondelete='set null', select=True, required=True),
        'name': fields.char('Quotation #', size=200, required=True),
        'attach': fields.boolean('(Quotation Attached?)'),
        'file': fields.binary('Quotation'),
        'date_iss': fields.date('Date'),
        'quot_type' : fields.selection([('rec','Received'),('sent', 'Sent')], 'Type', required=True, help='Was this quotation sent or received by AAG?'),
    }
    _defaults={
        # if you didn't fill out the date, by default it is going to be the current date (date you created this new row on the table)
        'date_iss': time.strftime('%Y-%m-%d'),
    }

quotation_file()

# adds a field to an already existing table
class res_partner(osv.osv):
    _description='partner'
    _inherit='res.partner' # this new class is just the same res.partner table but with an additional field.
    _name='res.partner'
    _columns={ # links to quotation.file table
        'quotation_id': fields.one2many('quotation.file', 'partner_id', 'Quotation Archive'),
    }
res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

