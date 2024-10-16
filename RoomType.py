import mysql.connector
import dbfunc

conn = dbfunc.getConnection()  
TABLE_NAME = 'RoomType'
DB_NAME = 'TestingDatabase'     

if conn is not None:    
    if conn.is_connected():  
        print('MySQL Connection is established')
        dbcursor = conn.cursor()    
        
       
        dataset = [
            ('Standard',),  
            ('Double',),    
            ('Family',),    
        ]
        

        INSERT_statement = "INSERT INTO RoomType(RoomTypeName) VALUES (%s)"
        
        for data in dataset:
            dbcursor.execute(INSERT_statement, data)
        
        conn.commit() 
        print('Data inserted successfully into the RoomType table.')
        
        dbcursor.close()    
        conn.close()    
    else:
        print('DB connection error')
else:
    print('DBFunc error')
