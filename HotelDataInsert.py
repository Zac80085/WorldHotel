#Name:Hein Zarni Naing
#StudentID:23005535

import mysql.connector, dbfunc
conn = dbfunc.getConnection()   
DB_NAME = 'HotelBooking'           
TABLE_NAME = 'Hotel'
INSERT_statement = 'INSERT INTO ' + TABLE_NAME + ' (\
    Address, City, PostCode, Capacity) VALUES (%s, %s, %s, %s);'    
if conn != None: 
    if conn.is_connected(): 
        print('MySQL Connection is established')                          
        dbcursor = conn.cursor()   
        dbcursor.execute('USE {};'.format(DB_NAME))
        dataset = [
        ('123 Moray Place', 'Aberdeen', 'AB1 2CD', 90),
        ('456 Lagan Road', 'Belfast', 'BT1 3EF', 80),
        ('789 Broad Street', 'Birmingham', 'B1 4FG', 110),
        ('101 Clifton Terrace', 'Bristol', 'BS1 5GH', 100),
        ('222 Welsh Street', 'Cardiff', 'CF1 6IJ', 90),
        ('333 Royal Mile', 'Edinburgh', 'EH1 7KL', 120),
        ('444 Argyle Street', 'Glasgow', 'G1 8MN', 140),
        ('555 Westminster Avenue', 'London', 'SW1 9OP', 160),
        ('666 Deansgate', 'Manchester', 'M1 0QR', 150),
        ('777 Quayside Road', 'Newcastle', 'NE1 1ST', 90),
        ('888 Wensum Way', 'Norwich', 'NR1 2UV', 90),
        ('999 Robin Hood Road', 'Nottingham', 'NG1 3PQ', 110),
        ('123 High Street', 'Oxford', 'OX1 4RT', 90),
        ('456 Marine Drive', 'Plymouth', 'PL1 2XY', 80),
        ('789 Mumbles Road', 'Swansea', 'SA1 3DE', 70),
        ('101 Sandbanks Avenue', 'Bournemouth', 'BH1 4FG', 90),
        ('222 Orchard Lane', 'Kent', 'CT1 5AB', 100)
    ]        
        dbcursor.executemany(INSERT_statement, dataset) 
        conn.commit()              
        print('INSERT query executed successfully.') 
        dbcursor.close()              
        conn.close() 
    else:
        print('DB connection error')
else:
    print('DBFunc error')
