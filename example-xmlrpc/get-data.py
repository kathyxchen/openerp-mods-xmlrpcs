import xmlrpclib

# if you want to test this with the demo database, use pwd = "admin", dbname = "demo" 
username = "admin" 
pwd = "start1234"
dbname = "AAG"

sock_common = xmlrpclib.ServerProxy("http://aag.advancedautomationgroup.com:8069/xmlrpc/common")

uid = sock_common.login(dbname, username, pwd)

sock = xmlrpclib.ServerProxy("http://aag.advancedautomationgroup.com:8069/xmlrpc/object")

args = [('vat', '=', 'ZZZZZZ')] # query clause
ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search', args)

# this script just prints out partner names that have a vat string matching 'ZZZZZZ'
# (gets relevant objects from the tables and prints for you to see accordingly)
print ids