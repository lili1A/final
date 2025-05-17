import pymysql
connection = pymysql.connect(
    host='localhost',  
    user='root',      
    password='Mersedese233', 
    db='Afire',       
    charset='utf8mb4'  
)

try:
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print("Tables in Afire Database:")
        for table in tables:
            print(table[0])

       
        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()
        
        print("\nTables data 'clients':")
        for client in clients:
            print(client)

finally:
    connection.close()  