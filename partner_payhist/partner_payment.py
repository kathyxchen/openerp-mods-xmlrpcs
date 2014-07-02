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

from openerp.osv import fields, osv
from openerp import pooler

class res_partner(osv.osv):
    _description='partner'
    _inherit='res.partner'
    _name='res.partner'
    _columns={
        'payment_id': fields.one2many('res.partner.payarch', 'partner_id', 'Customer Payment Archive'),
    }

res_partner()

class res_partner_payarch(osv.osv):
    _name='res.partner.payarch'
    _description='payment archive'
    _order='date_rec desc, balance desc, inv_date desc'
    _columns={
        'date_rec': fields.date('Date Received'),
        'po_num': fields.char('PO #', size=200),
        'invoice': fields.char('Invoice #', size=200),
        'inv_date' : fields.date('Invoice Date'),
        'mo_date' : fields.date('M/O Date'),
        'description': fields.char('Description', size=1000),
        'balance': fields.integer('Balance ($)'),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True, ondelete='cascade'),
    }

res_partner_payarch()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

