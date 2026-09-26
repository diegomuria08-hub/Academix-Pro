import pymysql

# Configuramos la conexión sin especificar la DB para poder crearla
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='YOKA2323',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # Create database
        sql = "CREATE DATABASE IF NOT EXISTS `academix-pro` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        cursor.execute(sql)
    connection.commit()
    print("Database 'academix-pro' ensured successfully.")
finally:
    connection.close()
