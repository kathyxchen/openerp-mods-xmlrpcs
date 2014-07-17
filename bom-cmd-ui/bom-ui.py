import xmlrpclib
import csv
import time
import sys
import re

domain = ''
username = ''
pwd = ''
dbname = '' 
sock_common = None
uid = None
sock = None

# a couple of helper functions
def checkEmpty(*arg):
    listBool = []
    for i in range(0, len(arg)):
        a = arg[i].strip()
        b = (a is '')
        listBool.append((a, b))
    notEmpty = [x for x, y in listBool if not y]
    if (len(notEmpty) == 0):
        return ''
    else:
        return '; '.join(notEmpty)

def checkName(x, y):
	if x.strip() is '':
		return y
	else:
		return x

def intersect(x, y):
	if x is not [] and y is not []:
		return [a for a in x if a in y]
	elif x is not []:
		return x[0]
	elif y is not []:
		return y[0]
	else: 
		return []

def check_uom():
	args = [('name', '=', 'pcs')]
	uom_list = sock.execute(dbname, uid, pwd, 'product.uom', 'search', args)
	if (len(uom_list) == 0):
		sock.execute(dbname, uid, pwd, 'product.uom', 'create', {'name': 'pcs', 'category_id': 1, 'factor': 1})
		uom_list = sock.execute(dbname, uid, pwd, 'product.uom', 'search', args)
	return uom_list[0]

def check_prod_categ():
	prod_categs = sock.execute(dbname, uid, pwd, 'product.category', 'search', [('name', '=', 'Materials')])
	if (len(prod_categs) == 0):
		sock.execute(dbname, uid, pwd, 'product.category', 'create', {'name': 'Materials', 'parent_id': 1})
		prod_categs = sock.execute(dbname, uid, pwd, 'product.category', 'search', [('name', '=', 'Materials')])
	return prod_categs[0]

def fix_nums(x, is_int):
	non_decimal = re.compile(r'[^\d.]+')
	x = non_decimal.sub('', x)
	if (x is '' or x == ''):
		return 0
	elif is_int:
		return int(x)
	else:
		return float(x)

def importProductData(fileName, argslist):
	if (argslist[0] == -1):
		print "Invalid: materials must have name or part number."
		return None
	try:
		reader = csv.reader(open(fileName,'rU'))
	except:
		print "Could not read CSV, check if path is correct."
	next(reader, None)
	for row in reader:
		print row[argslist[0]]
		if (argslist[1] == -1):
			nm = row[argslist[0]]
		else:
			nm = checkName(row[argslist[0]], row[argslist[1]])
		findargs = [('name', '=', nm)] # query clause
		name_ids = sock.execute(dbname, uid, pwd, 'product.product', 'search', findargs)
		if ((len(name_ids) != 0)):
			print 'Duplicate product. Ignored.'
			continue
		
		product_template = { # your own data & cols go here, this is once again based on field names, etc.
			'name': nm, 
			'standard_price': 0, # don't need for pcba
			'list_price': 0, # don't need for pcba
			'mes_type': 'fixed', # if you want to set defaults for these products
			'uom_id': check_uom(), # uom id for 'pcs' is 13. 
			'uom_po_id': check_uom(),
			'type': 'consu', # for pcbas, categorize as consumable because they are used for production of sellable product.
			'procure_method': 'make_to_order',
			'cost_method': 'standard',
			'supply_method': 'buy',
			'categ_id': check_prod_categ(),
       		'sale_ok': False,
			}
		if (argslist[1] != -1):
			product_template['description'] = row[argslist[1]]
		template_id = sock.execute(dbname, uid, pwd, 'product.template', 'create', product_template)
		product_product = {
			'product_tmpl_id': template_id,
			'active': True,
		}
		if (argslist[2] != -1):
			product_product['footprint'] = row[argslist[2]]
		if (argslist[3] != -1):
			product_product['manu_name'] = row[argslist[3]]
		if (argslist[4] != -1):
			product_product['stock_notes'] = row[argslist[4]]

		product_id = sock.execute(dbname, uid, pwd, 'product.product', 'create', product_product)
	print "Materials import successful."

def bomCreate(ids_bom, prod_qty, argslist, fileName):
	try:
		reader = csv.reader(open(fileName,'rU'))
	except:
		print "Could not read CSV, check if path is correct."
	count = 0
	next(reader, None)
	for row in reader:
		count += 1
		print row[argslist[0]] # this is just to verify that you are importing the correct information
		pqty = fix_nums(row[argslist[1]], True)
		if (pqty < 1):
			print row[argslist[0]] + ' PRODUCT QUANTITY IS 0. BOM CANN(T CONTAIN 0 QTY MATERIALS. IGNORED.'
			continue
		if (argslist[3] == -1):
			nm = row[argslist[0]]
		else: 
			nm = checkName(row[argslist[0]], row[argslist[3]])
		findName = [('name', '=', nm)] # query clause
		ids = sock.execute(dbname, uid, pwd, 'product.product', 'search', findName)
		if ids is []:
			print nm + ' NOT YET CREATED. IGNORED. PLEASE ADD TO BOM LATER.'
			continue
		parent = [('bom_id', '=', ids_bom)]
		bom_line_ids = sock.execute(dbname, uid, pwd, 'mrp.bom', 'search', parent)
		bom_lines_duplic = sock.execute(dbname, uid, pwd, 'mrp.bom', 'read', bom_line_ids, ['product_id'])

		if (nm in [ea['product_id'][1] for ea in bom_lines_duplic]):
			print 'DUPLICATE DETECTED'
			readQty = sock.execute(dbname, uid, pwd, 'mrp.bom', 'read', ea['id'], ['product_qty'])
			print readQty
			sock.execute(dbname, uid, pwd, 'mrp.bom', 'write', ea['id'], {'product_qty': readQty['product_qty'] + pqty})
			continue		
		
		mrp_bom = {
			'bom_id': ids_bom[0],
			'type': 'normal',
			'method': 'order',
			'product_id': ids[0],
			'product_qty': pqty,
			'product_uom': check_uom(),
        	'sequence': count
		}
		pn = fix_nums(row[argslist[4]], True)
		if (argslist[4] == -1):
			mrp_bom['production'] = prod_qty
		elif (pn < 1):
			mrp_bom['production'] = prod_qty
		else:
			mrp_bom['production'] = pn
		mrp_bom['unit_price'] = fix_nums(row[argslist[2]], False)
		bom_lines_id = sock.execute(dbname, uid, pwd, 'mrp.bom', 'create', mrp_bom)
	print "BOM import successful."

def importBOM(bom_nm, prod_qty, ref_code, argslist, fileName):	
	if ((argslist[0] == -1) or (argslist[1] == -1) or (argslist[2] == -1)):
		print 'INVALID: MATERIALS, PRICE, AND QUANTITIES MUST BE RECORDED.'
		print "Import failed.\n"
		return None
	args = [('name', '=', bom_nm)]
	prod_ids = sock.execute(dbname, uid, pwd, 'product.product', 'search', args)
	if (len(prod_ids) == 0):
		print "PRODUCT HAS NOT BEEN CREATED. PLEASE DO SO BEFORE CREATING YOUR BOM."
		print "Import failed.\n"
		return None
	args_bom = [('product_id', '=', prod_ids[0]), ('product_qty', '=', prod_qty), ('code', '=', ref_code)]
	ids_bom = sock.execute(dbname, uid, pwd, 'mrp.bom', 'search', args_bom)
	if (len(ids_bom) == 0):
		print 'Creating New BOM for ' + bom_nm
		new_bom_obj = {
			'type': 'normal',
			'method': 'order',
			'product_id': prod_ids[0],
			'product_qty': prod_qty,
			'product_uom': check_uom(),
		}
		if (ref_code == ''): 
			new_bom_obj['code'] = time.strftime('%Y%m%d')
		else:
			new_bom_obj['code'] = ref_code
		bom_id = sock.execute(dbname, uid, pwd, 'mrp.bom', 'create', new_bom_obj)
		bomCreate([bom_id], prod_qty, argslist, fileName)
	else: 
		bomCreate(ids_bom, prod_qty, argslist, fileName)

def exportBOM(bom_prod_name, prod_qty, bom_ref_code, fields_to_print):
	bom_prod_name = str(bom_prod_name)
	bom_ref_code = str(bom_ref_code)
	args = [('name', '=', bom_prod_name)]
	product_ids = sock.execute(dbname, uid, pwd, 'product.product', 'search', args)
	args_bom = [('product_id', '=', product_ids[0]), ('product_qty', '=', prod_qty), ('code','=',bom_ref_code)]
	ids_bom = sock.execute(dbname, uid, pwd, 'mrp.bom', 'search', args_bom)
	print ids_bom
	if (len(ids_bom) == 0):
		print "No BOM Found."
		return None
	bom_nm = ids_bom[0]
	find_bom_lines = [('bom_id', '=', bom_nm)]
	bom_lines = sock.execute(dbname, uid, pwd, 'mrp.bom', 'search', find_bom_lines)

	print len(bom_lines)
	data = sock.execute(dbname, uid, pwd, 'mrp.bom', 'read', bom_lines, fields_to_print)
	
	csvName = bom_prod_name + prod_qty + bom_ref_code + '.csv'
	writer = csv.writer(open(csvName,'wb'))
	writer.writerow(data[0].keys())
	for each in data:
		l = []
		for key, value in each.items():
			if (type(value) is list):
				l.append(value[1])
			else:
				l.append(value)
		writer.writerow(l)
	print "Export successful: " + csvName + " saved in current directory."

def inputCols(commonArgs):
	argslist = []
	print 'Enter corresponding column number (start from 1). If not present, input -1.'
	x = 0
	while (x < len(commonArgs)):
		a = raw_input("Column number for " + commonArgs[x] + ": ")
		if check(a, True):
			argslist.append(int(a)-1) 
			x += 1
	return argslist

def inputStrings(strArgs):
	answers = []
	x = 0
	while (x < len(strArgs)):
		a = raw_input(strArgs[x])
		if check(a, False):
			answers.append(a) 
			x += 1
	return answers

def check(x, is_int):
	if ((x.isdigit() and is_int) or (x == '-1')):
		return True
	else:
		if (str(x) == 'menu'):
			return cmdInterface()
		elif (str(x) == 'login'):
			return start()
		elif (str(x) == 'exit'):
			sys.exit()
		elif (not is_int):
			return True
		else:
			print "   Invalid input, try again."
			return False

def errorMsg():
	print "Type 'menu' to return to Menu, 'login' to return to Login, 'exit' to Exit."
	x = raw_input(">> ")
	check(x, False)

def cmdInterface():
	print "\n(Type 'menu' to return to Menu, 'login' to return to Login, 'exit' to Exit.)"
	exit = '0'
	while (exit != 'exit'):
		choice = raw_input("\n1) Importing Materials?\n2) Importing BOM?\n3) Exporting BOM?\n>> Integer Input:")
		check(choice, True)
		if (choice is '1'):
			commonArgs = ['Name/Part Number', 'Description', 'Footprint', 'Manufacturer', 'Notes']
			argslist = inputCols(commonArgs)		
			fileName = raw_input(">> Path to CSV File (must end in '.csv'): ")
			if check(fileName, False):
				try:
					print "ATTEMPTING IMPORT. PRESS CTRL + C TO END."
					importProductData(fileName, argslist)
				except:
					print "ERROR: ", sys.exc_info()[0]
					print "Import failed."
					errorMsg()
		elif (choice is '2'):
			print "\nFOR RE-IMPORTS: If previous import failed mid-way, DELETE and MAKE A NEW BOM ON OPENERP before loading CSV. Otherwise, quantities will be DOUBLED.\n"
			commonArgs = ['Name/Part Number', 'Qty Per Board', 'Unit Price', 'Description', 'Production Qty']
			argslist = inputCols(commonArgs)
			bom_traits = [">> Path to CSV File (must end in '.csv'): ", '>> Product: ', '>> Quantity: ', '\n(Set your own or press Enter to assign the default code, which is the current date.)\n>> Reference Code: ']
			answers = inputStrings(bom_traits)
			try:
				print "ATTEMPTING IMPORT. PRESS CTRL + C TO END."
				importBOM(answers[1], answers[2], answers[3], argslist, answers[0])
			except:
				print "ERROR: ", sys.exc_info()[0]
				print "Import failed."
				print "WARNING: If failure occurred mid-import, DELETE and MAKE A NEW BOM before attempting another import. Otherwise, quantities will be DOUBLED."
				errorMsg()
		elif (choice is '3'):
			print "Find requested information on the OpenERP web client. This is used to export the correct BOM."
			bom_traits = [">> Product: ", ">> Quantity: ", ">> Reference Code: "]
			answers = inputStrings(bom_traits)
			print """\n(Make sure field names are accurate--enter Developer Mode to view fields.)\nList of commonly exported fields:\nproduct_id, product_qty, description, production, unit_price,\nfootprint, description, vol_demanded, manu_name, per_board,\next_price\n"""
			print "Separate by commas. Do not use quotations, brackets, etc."
			fields = raw_input(">> List of Fields: ")
			listFields = fields.split(",")
			listFields = [x.strip() for x in listFields]
			try:
				exportBOM(answers[0], answers[1], answers[2], listFields)
			except: 
				print "ERROR: ", sys.exc_info()[0]
				print "Export failed."
				errorMsg()
		else:
			return cmdInterface()
		exit = raw_input(">> Type 'exit' to exit, 'c' to continue: ")

def changeDomain():
	d = raw_input("\n>> New domain address: ")
	if (d == 'exit'):
		return start()
	print "Domain name changed to: " + d + "."
	while True:
		choice = raw_input(">> Type 'y' to confirm, 'n' to change, or 'exit' to exit without saving: ")
		if (choice == 'y'):
			with open('domainname.csv','wb') as csvFile:
				writer = csv.writer(csvFile)
				writer.writerow([str(d)])
			return start()
		elif (choice == 'n'):
			return changeDomain()
		elif (choice == 'exit'):
			return start()
		else:
			print "Invalid input, try again."

def start():
	r = csv.reader(open('domainname.csv', 'rU'))
	global domain
	domain = r.next()[0]
	print "\n(Press CTRL + C to exit)"
	print "If domain has changed from: " + domain + ", please type 'domain' to change this."
	print "OpenERP Database Access Information:"
	global username
	username = raw_input(">> Username: ")
	if (username == 'domain'):
		changeDomain()
	global pwd
	pwd = raw_input(">> Password: ")
	global dbname
	dbname = raw_input(">> Database Name: ")
	cont = False
	try:
		global sock_common
		sock_common = xmlrpclib.ServerProxy("http://" + domain + ":8069/xmlrpc/common")
		global uid
		uid = sock_common.login(dbname, username, pwd)
		global sock
		sock = xmlrpclib.ServerProxy("http://" + domain + ":8069/xmlrpc/object")
		cont = True
	except:
		print "\nLogin Failed. Try again."
		return start()
	if cont:
		cmdInterface()
start()
