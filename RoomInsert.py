#Name:Hein Zarni Naing
#StudentID:23005535
import dbfunc

def get_hotel_capacities(conn):
    capacities = {}
    cursor = conn.cursor()
    cursor.execute("SELECT HotelID, Capacity FROM Hotel")
    for (HotelID, Capacity) in cursor:
        capacities[HotelID] = Capacity
    cursor.close()
    return capacities

def get_room_type_ids(conn):
    room_type_ids = {}
    cursor = conn.cursor()
    cursor.execute("SELECT RoomTypeID, RoomTypeName FROM RoomType")
    for (RoomTypeID, RoomTypeName) in cursor:
        room_type_ids[RoomTypeName] = RoomTypeID
    cursor.close()
    return room_type_ids

def insert_room_data(conn, capacities, room_type_ids):
    cursor = conn.cursor()
    for hotel_id, capacity in capacities.items():
        room_number = 100
        standard_count = int(0.3 * capacity)
        double_count = int(0.5 * capacity)
        family_count = capacity - standard_count - double_count
        
        for _ in range(standard_count):
            room_type_id = room_type_ids['Standard']
            cursor.execute(
                "INSERT INTO Room (HotelID, RoomNumber, RoomTypeID) VALUES (%s, %s, %s)",
                (hotel_id, room_number, room_type_id)
            )
            room_number += 1
        
        for _ in range(double_count):
            room_type_id = room_type_ids['Double']
            cursor.execute(
                "INSERT INTO Room (HotelID, RoomNumber, RoomTypeID) VALUES (%s, %s, %s)",
                (hotel_id, room_number, room_type_id)
            )
            room_number += 1
        
        for _ in range(family_count):
            room_type_id = room_type_ids['Family']
            cursor.execute(
                "INSERT INTO Room (HotelID, RoomNumber, RoomTypeID) VALUES (%s, %s, %s)",
                (hotel_id, room_number, room_type_id)
            )
            room_number += 1
        
    conn.commit()
    cursor.close()

conn = dbfunc.getConnection() 

if conn is not None:
    if conn.is_connected():
        print('MySQL Connection is established')
        
        capacities = get_hotel_capacities(conn)
        room_type_ids = get_room_type_ids(conn)
        insert_room_data(conn, capacities, room_type_ids)
        
        print('Data inserted successfully into the Room table.')
        
        conn.close()
    else:
        print('DB connection error')
else:
    print('DBFunc error')
