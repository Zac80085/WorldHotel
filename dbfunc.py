#Code from practical
#Name:Hein Zarni Naing
#StudentID:23005535
import mysql.connector
from mysql.connector import errorcode

hostname    = "localhost"
username    = "root"
passwd  = "Heinzarni123"
database = "HotelBooking"

def getConnection():    
    try:
        conn = mysql.connector.connect(host=hostname,                              
                              user=username,
                              password=passwd,
                              database = database)  
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('User name or Password is not working')
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print('Database does not exist')
        else:
            print(err)                        
    else:
        print("esterblished connection")   
        return conn
                
