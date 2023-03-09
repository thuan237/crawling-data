import requests
import pandas as pd
import json
import mysql.connector
from fastapi import FastAPI, Query, Depends
import db_account as account

app = FastAPI()

connectDb = mysql.connector.connect(
    host=account.db_host, database=account.db_name, user=account.db_username, password=account.db_password)

cursor = connectDb.cursor(dictionary=True)


def get_all_category():
    query = 'select * from category'
    cursor.execute(query)
    result = cursor.fetchall()
    return result


@app.get("/api/category/all")
def get_all_category_endpoint():
    result = get_all_category()
    return result


def get_book_of_genres(genres):
    query = """SELECT pro.id, pro.product_name, pro.product_price 
               FROM product as pro, option as opt, product_option as pr_op, attribute as att 
               WHERE pro.id = pr_op.product_id and 
                     opt.id = pr_op.option_id and 
                     att.id = opt.attr_id and 
                     att.code = "genres" and 
                     opt.label like """ + genres
    cursor.execute(query)
    result = cursor.fetchall()
    return result


@app.get("/api/book/genres")
def get_book_of_genres_endpoint(genres: str):
    result = get_book_of_genres(genres)
    return result


def get_book_by_price(min, max):
    query = 'select * from product where product_finalprice>=' + \
        min+'and product_finalprice<='+max
    cursor.execute(query)
    result = cursor.fetchall()
    return result


@app.get("/api/book/price")
def get_book_of_genres_endpoint(min: int, max: int):
    result = get_book_by_price(min, max)
    return result

# database
def get_data(query):
    cursor.execute(query)
    return cursor.fetchall()  

@app.get("/api/attribute-codes")
def get_all_attr_codes():
    query = "select code from attribute"
    rs = pd.DataFrame(get_data(query))
    if('code' in rs.columns):
        return rs['code'].values.tolist()  
    return []

@app.get("/api/option")
def get_option(code: str):
    query = "SELECT code ,o.id as id FROM options o join attribute a on a.id = o.attr_id and a.code = '{}'".format(code)
    return get_data(query)

@app.get("/api/cate-childlest-list")
def get_cate_childlest():
    query = "select id from category where id not in (select parent_category from category)"
    rs = pd.DataFrame(get_data(query))
    return rs['id'].values.tolist() 

@app.get("/api/product-id-list")
def get_product_id_list():
    query = "select id from product"
    rs = pd.DataFrame(get_data(query))
    if('id' in rs.columns):
        return rs['id'].values.tolist()  
    return []

@app.get("/api/check-id")
def check_id( table_name, _id):
    query = "select id from " + table_name +" where id = " + _id
    return len(get_data(query)) > 0 

@app.get("/api/check-product-option")
def check_product_options(product_id, option_id):
    query = "select * from product_option where product_id = {} and  option_id = {}".format(product_id, option_id)
    return len(get_data(query)) > 0 

@app.post("/api/insert")
def insert_data(table_name: str, data: dict):
    keys = data.keys()
    col = ', '.join(keys)
    row = ', '.join(['%s'] * len(keys))
    insert = "insert  into {} ({}) values ({})".format(table_name, col, row)
    row_data = list(data.values())
    cursor.execute(insert, row_data)
    connectDb.commit()
    return data

@app.get("/api/get-all-product")
def get_all_product():
    sql = "SELECT * FROM product"
    cursor.execute(sql)
    return cursor.fetchall()

@app.post("/api/update-craw-product")
def update_craw_product(idpd, data: dict):
    try:
        # Truy van cap nhat tat ca ban ghi trong bang "product"
        sql = "UPDATE product SET item_code = '" + data['item_code']+"', author = '"+data['author']+"', publisher = '"+data['publisher']
        sql = sql + "', publish_year = '"+data['publish_year']+"', weight = "+data['weight']+", size = '"+data['size']+"', page_number = "+data['page_number']
        sql = sql + ", material = '"+data['material']+"', specification = '"+data['specification']+"', warning_info = '"+data['warning_info']
        sql = sql + "', use_guide = '"+data['use_guide']+"', translator = '"+data['translator']+"' WHERE id = " + str(idpd)
        # Thuc thi cau truy van 
        cursor.execute(sql)
        # Xac thuc viec cap nhat ban ghi khoi bang "product"
        connectDb.commit()
        rs = "Ban ghi da duoc cap nhat!"
    except:# Truong hop co loi cap nhat ban ghi trong bang
        rs = "Khong the cap nhat ban ghi trong bang!"
    return rs

# # Cách 2
@app.get("/api/get-all")
def get_all(table_name: str):
    query = "select * from " + table_name
    return get_data(query)

# @app.post("/api/insert-list")
# def insert_list_data(table_name: str, data: list):
#     data = pd.DataFrame(data)    
#     keys = data.keys()
#     col = ', '.join(keys)
#     row = ', '.join(['%s'] * len(keys))
#     insert = "insert  into {} ({}) values ({})".format(table_name, col, row)
#     values = [tuple(row.values) for i,row in data.iterrows()]
#     cursor.executemany(insert, values)
#     connectDb.commit()
#     return data.to_dict('records')
