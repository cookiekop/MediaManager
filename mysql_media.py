import mysql.connector

class MediaSQL:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if MediaSQL._instance is None: 
            MediaSQL._instance = super().__new__(cls) 
        return MediaSQL._instance

    def __init__(self, host="localhost", user="root", passwd="", db_name="my_db"):
        self._mydb = mysql.connector.connect(host=host, \
                                             user=user, \
                                             auth_plugin = 'mysql_native_password', \
                                             passwd=passwd)
        cursor = self._mydb.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS {};'.format(db_name))
        cursor.execute('use {};'.format(db_name))

    def create_tb(self, tb_name:str, cols, col_ds, col_type):
        # (imdb_id VARCHAR(20) PRIMARY KEY,rating INT NOT NULL,update_time INT NOT NULL)DEFAULT CHARSET=utf8"
        col_num = len(cols)
        assert(len(col_ds) == len(col_type) == col_num)
        definition = "("
        for i in range(col_num):
            definition += "{} {} {}".format(cols[i], col_ds[i], col_type[i])
            if i == col_num - 1: definition += ')DEFAULT CHARSET=utf8'
            else: definition += ','
        cursor = self._mydb.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS {}{}".format(tb_name, definition))
        
    def query(self, tb_name, arg):
        cursor = self._mydb.cursor()
        cursor.execute("SELECT * FROM {} WHERE {}".format(tb_name, arg))
        return cursor.fetchall()

    def insert(self, tb_name, cols, vals):
        cursor = self._mydb.cursor()
        val_ph = ",".join(["%s" for _ in range(len(cols))])
        sql = "INSERT IGNORE INTO {} ({}) VALUES ({})".format(tb_name, ",".join(cols), val_ph)
        cursor.execute(sql, vals)
        self._mydb.commit()

    def update(self, tb_name, col, new_val, prim_key, id, ts):
        cursor = self._mydb.cursor()
        sql = "UPDATE {} SET {} = %s WHERE {} = %s".format(tb_name, col, prim_key)
        cursor.execute(sql, (new_val, id))
        self._mydb.commit()
        if ts is not None: self.update(tb_name, 'update_time', ts, prim_key, id, None)
    
    def remove(self, tb_name, arg):
        cursor = self._mydb.cursor()
        cursor.execute("DELETE FROM {} WHERE {}".format(tb_name, arg))
        self._mydb.commit()