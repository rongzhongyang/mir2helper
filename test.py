import os
import sqlite3


def update_constant_value(self, 主备: str, 合备: str):
    db_version = self.data['数据库版本']
    if len(db_version) < 2:
        return
    try:
        db_str = rf"{主备}Mir200\M2Data\ApexM2Data.DB"
        conn = sqlite3.connect(db_str)
        cursor = conn.cursor()
        sql_str = rf"update db_constant set ConstValue = {db_version} where ConstName = 'version'"
        cursor.execute(sql_str)
        conn.commit()
        conn.close()
    except Exception as e:
        self.msg.emit(rf"{db_str} {str(e)}")
    try:
        db_str = rf"{合备}Mir200\M2Data\ApexM2Data.DB"
        conn = sqlite3.connect(db_str)
        cursor = conn.cursor()
        sql_str = rf"update db_constant set ConstValue = {db_version} where ConstName = 'version'"
        cursor.execute(sql_str)
        conn.commit()
        conn.close()
    except Exception as e:
        self.msg.emit(rf"{db_str} {str(e)}")

if __name__ == '__main__':
    update_constant_value(r'D:\hjls176')