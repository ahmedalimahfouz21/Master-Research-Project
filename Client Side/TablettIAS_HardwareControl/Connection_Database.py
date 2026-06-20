import sys
import time
import mysql.connector as mariadb

class Connection_Database():

    def __init__(self):
        try:
            
            self.con = mariadb.connect(host = 'localhost' , user='root', passwd='tantum', db='mytantum', port = '3306', charset = 'utf8')
            self.cur = self.con.cursor()
            self.cur.execute('SET NAMES utf8;')
            self.cur.execute('SET CHARACTER SET utf8;')
            self.cur.execute('SET character_set_connection=utf8;')
        except mariadb.Error as e:
            print("Error %d: %s" % (e.args[0], e.args[1]))
            #sys.exit(1)



    def update_extraction_pillfall(self, extractID, timestamp, status):
        try:
            formatted_date = time.strftime('%Y-%m-%d %H:%M:%S' , timestamp)
            sql_update = "UPDATE extraction_times SET time_pills_detected = %s, status = %s WHERE id_extraction_times = %s"
            values = (formatted_date, status, extractID)
            self.cur.execute(sql_update, values)
            self.con.commit()
        except mariadb.Error as e:
            print("Can't access database -> pill fall not updated")

    def update_extraction_removed(self, extractID, timestamp, status):
        try:
            formatted_date = time.strftime('%Y-%m-%d %H:%M:%S' , timestamp)
            sql_update = "UPDATE extraction_times SET time_removed = %s, status = %s WHERE id_extraction_times = %s"
            values = (formatted_date, status, extractID)
            self.cur.execute(sql_update, values)
            self.con.commit()
        except mariadb.Error as e:
            print("Can't access database -> pill removed not updated")

    def update_extraction_opened(self, extractID, timestamp, status):
        try:
            formatted_date = time.strftime('%Y-%m-%d %H:%M:%S' , timestamp)
            sql_update = "UPDATE extraction_times SET time_opened = %s, status = %s WHERE id_extraction_times = %s"
            values = (formatted_date, status, extractID)
            self.cur.execute(sql_update, values)
            self.con.commit()
        except mariadb.Error as e:
            print("Can't access database -> pill removed not updated")


if __name__ == '__main__':
    myDB = Connection_Database()
