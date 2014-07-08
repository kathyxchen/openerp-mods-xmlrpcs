import xmlrpclib
import csv

# if you want to import data into the demo database as a test first, use pwd = "admin", dbname = "demo" 
username = "admin" 
pwd = "start1234"
dbname = "AAG"

sock_common = xmlrpclib.ServerProxy("http://aag.advancedautomationgroup.com:8069/xmlrpc/common")

uid = sock_common.login(dbname, username, pwd)

sock = xmlrpclib.ServerProxy("http://aag.advancedautomationgroup.com:8069/xmlrpc/object")


# (replace this w/ your path to the CSV you want to import)
# 'rU' can quite often be changed to 'rb' depending on format
reader = csv.reader(open('testProd.csv','rU'))

for row in reader:
	print row[1] # this is just to verify that you are importing the correct information
	product_template = { # your own data & cols go here, this is once again based on field names, etc.
		'name': row[1], # assign corresponding cols accordingly
		'standard_price': row[2],
		'list_price': row[2],
		'mes_type': 'fixed', # if you want to set defaults for these products
		'uom_id': 1,
		'uom_po_id': 1,
		'type': 'product',
		'procure_method': 'make_to_stock',
		'cost_method': 'standard',
		'categ_id': 1,
        'description' : row[1],
		}
	template_id = sock.execute(dbname, uid, pwd, 'product.template', 'create', product_template)

	# the product module requires a product_template be made before the product itself is created
	# this is likely not the case for most modules
	product_product = {
		'product_tmpl_id': template_id,
		'default_code': row[3],
		'active': True,
	}
	product_id = sock.execute(dbname, uid, pwd, 'product.product', 'create', product_product)