import sqlite3

conn = sqlite3.connect('canteen.db')

# conn.execute("insert into COMPANY(id,name,age,address,salary) values(1,'name',26,'kalapark',1200)")
# conn.commit()
value = conn.execute("select * from Canteen")
for i in value:
    print(i)

conn.close()