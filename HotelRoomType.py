#Name:Hein Zarni Naing
#StudentID:23005535

import dbfunc

conn = dbfunc.getConnection()   
TABLE_NAME = 'Hotel_RoomType'
DB_NAME = 'TestingDatabase'    

if conn is not None:    
    if conn.is_connected():  
        print('MySQL Connection is established')
        dbcursor = conn.cursor()   
        
        dataset = [
            (1, 1, 140, 70),  
            (2, 1, 130, 70),  
            (3, 1, 150, 75), 
            (4, 1, 140, 70),  
            (5, 1, 130, 70), 
            (6, 1, 160, 80), 
            (7, 1, 150, 75), 
            (8, 1, 200, 100),
            (9, 1, 180, 90),
            (10, 1, 120, 70),  
            (11, 1, 130, 70),  
            (12, 1, 130, 70),  
            (13, 1, 180, 90), 
            (14, 1, 180, 90),
            (15, 1, 130, 70), 
            (16, 1, 130, 70),
            (17, 1, 140, 80)
        ]
        
        capacities = {}
        dbcursor.execute("SELECT HotelID, Capacity FROM Hotel")
        for row in dbcursor.fetchall():
            capacities[row[0]] = row[1]
        
        for data in dataset:
            hotel_id, room_type_id, standard_peak_price, standard_off_peak_price = data
            hotel_capacity = capacities.get(hotel_id, 0)
            standard_capacity = int(0.3 * hotel_capacity) 
            double_capacity = int(0.5 * hotel_capacity)   
            family_capacity = int(0.2 * hotel_capacity)            
            dbcursor.execute("INSERT INTO Hotel_RoomType (HotelID, RoomTypeID, PeakSeasonPrice, OffPeakSeasonPrice) VALUES (%s, %s, %s, %s)",
                            (hotel_id, room_type_id, standard_peak_price, standard_off_peak_price))
                
        conn.commit()   
        print('Data inserted successfully into the Hotel_RoomType table.')
        
        dbcursor.close()    
        conn.close()    
    else:
        print('DB connection error')
else:
    print('DBFunc error')
