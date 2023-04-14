# -*- coding: utf-8 -*-
# @Time : 2023/4/9 21:42
# @Author : JIQ
# @Email : jiq1314an@qq.com
import pymysql


def get_conn():
    """
    :return: 连接，游标
    """
    # 创建连接
    conn = pymysql.connect(host="localhost",
                           user="root",
                           password="123456",
                           db="mos",
                           charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor


def close_conn(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def query(sql, *args):
    """
    封装通用查询
    :param sql:
    :param args:
    :return: 返回查询到的结果，((),(),)的形式
    """
    con, cursor = get_conn()
    cursor.execute(sql, args)
    res = cursor.fetchall()
    close_conn(con, cursor)
    return res
