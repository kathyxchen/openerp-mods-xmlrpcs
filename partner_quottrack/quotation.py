# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import pooler
import time

class sale_order(osv.osv):
    _inherit='sale.order'
    _name='sale.order'
    _description='Sales Order'
    _columns={
        'partner_quote_no': fields.many2one('quotation.file', 'Quotation #', readonly=True, states={'draft': [('readonly', False)]}),
    }

sale_order()

class quotation_file(osv.osv):
    _name='quotation.file' 
    _description='quotation module'
    _order='partner_id, date_iss desc, quot_type'
    _columns={
        'partner_id': fields.many2one('res.partner', 'Partner Name', ondelete='set null', select=True, required=True),
        'name': fields.char('Quotation #', size=200, required=True),
        'attach': fields.boolean('(Quotation Attached?)', help='See sidebar on the right for the attached quotation.'),
        'file': fields.binary('Quotation', help='Note this ONLY works on client, not web'),
        'date_iss': fields.date('Date'),
        'quot_type' : fields.selection([('rec','Received'),('sent', 'Sent')], 'Type', required=True, help='Was this quotation sent or received by AAG?'),
    }
    _defaults={
        'date_iss': time.strftime('%Y-%m-%d'),
    }

quotation_file()

class res_partner(osv.osv):
    _description='partner'
    _inherit='res.partner'
    _name='res.partner'
    _columns={
        'quotation_id': fields.one2many('quotation.file', 'partner_id', 'Quotation Archive'),
    }

res_partner()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

