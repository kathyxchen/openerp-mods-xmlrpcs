import xmlrpclib
import csv

# change this information to match your database
username = "admin"
pwd = "admin"
dbname = "demo"

sock_common = xmlrpclib.ServerProxy("http://aag.advancedautomationgroup.com:8069/xmlrpc/common")

uid = sock_common.login(dbname, username, pwd)

sock = xmlrpclib.ServerProxy("http://aag.advancedautomationgroup.com:8069/xmlrpc/object")

# select the objects you want to read information from
# (in this case, partners that are suppliers)
record_ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search', [('supplier', '=', True)])

# list of fields you want to view
fields = ['name', 'active', 'vat', 'ref'] #fields to read

# read them into the data list
data = sock.execute(dbname, uid, pwd, 'res.partner', 'read', record_ids, fields)

# print!
for each in data:
    print each # where each is a dictionary

# also write to a csv.
# replace 'dict.csv' with path to whatever empty csv you want to write to
writer = csv.writer(open('dict.csv', 'wb'))
writer.writerow(data[0].keys())
for each in data:
    l = []
    for key, value in each.items():
        l.append(value)
    writer.writerow(l)