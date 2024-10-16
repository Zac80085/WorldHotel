#Name:Hein Zarni Naing
#StudentID:23005535

import dbfunc

conn = dbfunc.getConnection()  
DB_NAME = 'HotelBooking' 

UPDATE_statement = 'UPDATE Room SET AvailabilityStatus = %s WHERE RoomID = %s;'

if conn is not None:  
    if conn.is_connected(): 
        print('MySQL Connection is established')
        dbcursor = conn.cursor() 
        dbcursor.execute('USE {};'.format(DB_NAME))  

        data = ('Yes', 1)
        
        dbcursor.execute(UPDATE_statement, data)  
        conn.commit() 
        print('UPDATE query executed successfully.')

        dbcursor.close()              
        conn.close()  
    else:
        print('DB connection error')
else:
    print('DBFunc error')
