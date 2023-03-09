# -*- coding: utf-8 -*-
import pandas as pd
import json
import requests
from lxml import html
from bs4 import BeautifulSoup
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

data_url = 'https://www.fahasa.com/fahasa_catalog/product/loadCatalog?category_id='
api_url = 'http://127.0.0.1:8000/api/'
check_url1 = api_url + 'check-id?table_name={}&_id={}'
check_url2 = api_url + 'check-product-option?product_id={}&option_id={}'
url_product_list = data_url + '{}&limit={}'


t = time.time()

#lấy dữ liệu từ api
def get_data_from_api(url,att):
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    response = requests.get(url, headers=headers)
    json = response.json()
    if(type(json[att])==list):
        df = pd.DataFrame(json[att])
    else:
        df = json[att]
    return df

#check exists
def is_exists(url):
    res = requests.get(url)
    return json.loads(res.text)

#insert data
def insert(table_name, data):
    url = api_url + 'insert?table_name='+table_name
    res = requests.post(url, data=json.dumps(data))
    print(res.text)
    return json.loads(res.text)

#crawl categories
# new_categories = []
# all_category = ['2']
# df = get_data_from_api(data_url + "2",'category')
# df['parent_category'] = '2'
# if(not is_exists(check_url1.format('category', '2'))):
#       new_categories = [insert('category', df.iloc[0].to_dict())]

def insert_list(table_name, data):
    url = api_url + 'insert-list?table_name='+table_name
    res = requests.post(url, data=json.dumps(data))
    print(res.text)
    return json.loads(res.text)

#get request
def getData(url):
    res = requests.get(url)
    return json.loads(res.text)

#bat dong bo
def runner(data, func):
    threads= []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in data:
            threads.append(executor.submit(func, i))
        for task in as_completed(threads):
            print(task.result()) 

#crawl categories
# old_categories = getData(api_url + 'get-all?table_name=category')
# new_categories = []
# all_cate_ids = [2]

def get_cate(data):
    _id, parent_id = data
    df = get_data_from_api(data_url + str(_id), 'children_categories')
    if(not 'id' in df.columns):
        return  
    
    new_cate = get_data_from_api(data_url + str(_id),'category')
    new_cate['parent_category'] = _id
    new_cate['id'] = int(new_cate['id'])
    new_cate in old_categories and new_categories.append(new_cate)
    print(len(all_cate_ids))
    cur_cate_ids = df['id'].values.tolist()
    new_cate_ids = [i for i in cur_cate_ids if i not in all_cate_ids]
    
    if(new_cate_ids == []):
        return 
    all_cate_ids.extend(new_cate_ids)
    next_cate = [[i, _id] for i in new_cate_ids]
    runner(next_cate, get_cate)
        
# get_cate([2, 2])    
#dat lenh insert o day
# print(all_cate_ids)

# Crawl attributes
# attributes = get_data_from_api(data_url+"2",'attributes')[['id', 'code', 'label']]
# new_attributes = [insert('attribute', row.to_dict()) for index, row in attributes.iterrows() if not is_exists(check_url1.format('attribute', row['id']))]
# print(new_attributes)

# Crawl options

# Crawl attributes
# old_attributes = getData(api_url + 'get-all?table_name=attribute')
# cur_attributes = get_data_from_api(data_url+"2",'attributes')[['id', 'code', 'label']]
# cur_attributes['id'] = pd.to_numeric(cur_attributes['id'])
# new_attributes = [i for i in cur_attributes.to_dict('records') if i not in old_attributes]
# print('new attributes')
# print(new_attributes)

# #Crawl options
# old_options = getData(api_url + 'get-all?table_name=options')

# new_options = []

def filter_options(row):
    row = row._asdict()
    options = pd.DataFrame(row['options'])[['id', 'label']]
    options['attr_id'] = int(row['id'])
    options['id'] = pd.to_numeric(options['id'])
    
    cur_options = options.to_dict('records')
    data = [i for i in cur_options if i not in new_options]
    new_options.extend(data)

def get_options(_id):
    df = get_data_from_api(data_url + str(_id),'attributes')
    if('id' and 'options' not in df.columns):
        return
    for index, row in df[['id', 'options']].iterrows():
        options = pd.DataFrame(row['options'])[['id', 'label']]
        options['attr_id'] = int(row['id'])
        options['id'] = pd.to_numeric(options['id'])
        
        cur_options = options.to_dict('records')
        data = [i for i in cur_options if i not in new_options and i not in old_options]
        new_options.extend(data)
    return data
    
        
# cate_ids = getData(api_url + "cate-childlest-list")
# runner(cate_ids, get_options)
#dat lenh insert o day
# print('new options')
# print(new_options)

#crawl product_options
# old_product_option = getData(api_url + 'get-all?table_name=product_option')
# new_product_option = []
# attr_codes = getData(api_url + "attribute-codes")
# option_ids = sum([getData(api_url + "option?code="+code) for code in attr_codes], [])

def crawl_product_option(option):
    url = data_url+'{}&filters%5B{}%5D={}'.format(2, option['code'], option['id'])  
    total = get_data_from_api(url,'total_products')
    print(url)
    products = get_data_from_api(url + '&limit=' + str(total),'product_list')
    if(not 'product_id' in products.columns):
        return
    product_ids = products[['product_id']]
    product_ids['product_id'] = pd.to_numeric(product_ids['product_id'])
    product_ids['option_id']  = option['id']
    
    cur_product_option = product_ids.to_dict('records')
    data = [i for i in cur_product_option if i not in old_product_option]
    new_product_option.extend(data)
    print(len(new_product_option))
            
# runner(option_ids, crawl_product_option)
#dat lenh insert o day
# print ("done in ", time.time()- t)
        

#----------------------Product_list-------------------------------

# Lấy danh sách sản phẩm về
cate_child_id =  getData(api_url + "cate-childlest-list")
#print(cate_child_id)
old_product_id = getData(api_url + "product-id-list")
#print(old_product_id)
new_products = []

def get_data_product(category_id):
    try:
        url = data_url + str(category_id)
        #print(category_id)
        total = get_data_from_api(url, 'total_products')
        url = url_product_list.format(category_id,total)
        df = get_data_from_api(url,'product_list')   
        df.fillna(value=0, inplace=True)
        df['category_id'] = category_id
        df['product_price'] =  [int(str(p).replace('.', '')) for p in df['product_price']]
        df['product_finalprice'] =  [int(str(p).replace('.', '')) for p in df['product_finalprice']]
        df.rename(columns = {'product_id':'id'}, inplace=True)
        df['id'] = pd.to_numeric(df['id'])
        new_data = [row for row in df.to_dict('records') if row['id'] not in old_product_id]
        new_products.extend(new_data)
        return "cate_id: {} || Total of this cate_id: {}|| Current total: {}".format(category_id,total,len(new_products))
    except:
        print("Loi be oi!")
    

runner(cate_child_id, get_data_product)
#print(new_products)

#--------------------------------------------Update Request Product----------------------------------------
#Request thông tin của sản phẩm trên web
def crawNewBook(url):
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-Agent': 'My User Agent 1.0',
        }
    )
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    #Thông tin sản phẩm
    book = {}
    product_info = soup.select_one("#product_view_info > div.product_view_tab_content_ad > div.product_view_tab_content_additional > table > tbody")
    try:
        item_code = product_info.find("td", class_="data_sku").text.strip()
        book["item_code"] = item_code
    except:
        book["item_code"] = "null"
    try:
        author = product_info.find("td", class_="data_author").text.strip()
        book["author"] = author
    except:
        book["author"] = "null"
    try:
        publisher = product_info.find("td", class_="data_publisher").text.strip()
        book["publisher"] = publisher
    except:
        book["publisher"] = "null"
    try:
        publish_year = product_info.find("td", class_="data_publish_year").text.strip()
        book["publish_year"] = publish_year
    except:
        book["publish_year"] = "null"
    try:
        weight = product_info.find("td", class_="data_weight").text.strip()
        book["weight"] = weight
    except:
        book["weight"] = "null"
    try:
        size = product_info.find("td", class_="data_size").text.strip()
        book["size"] = size
    except:
        book["size"] = "null"
    try:
        page_number = product_info.find("td", class_="data_qty_of_page").text.strip()
        book["page_number"] = page_number
    except:
        book["page_number"] = "null"
    try:
        material = product_info.find("td", class_="data_material").text.strip()
        book["material"] = material
    except:
        book["material"] = "null"
    try:
        #specification description
        specification = ""
        specifications = soup.select("#desc_content > p")
        for des in specifications:
            specification += des.text.strip() + "\n"
        book["specification"] = specification[:250] + "..."
    except:
        book["specification"] = "null"
    try:
        warning_info = product_info.find("td", class_="data_warning").text.strip()
        book["warning_info"] = warning_info
    except:
        book["warning_info"] = "null"
    try:
        #use_guide directions
        use_guide = product_info.find("td", class_="data_directions").text.strip()
        book["use_guide"] = use_guide
    except:
        book["use_guide"] = "null"
    try:
        translator = product_info.find("td", class_="data_translator").text.strip()
        book["translator"] = translator
    except:
        book["translator"] = "null"
    return book

#Get tất cả sản phẩm
def get_all_product():
    url = api_url + 'get-all-product'
    res = requests.get(url)
    return json.loads(res.text)

#Cập nhật thông tin một sản phẩm
def update_craw_product(idpd, data):
    url = api_url + 'update-craw-product?idpd='+str(idpd)
    res = requests.post(url, data=json.dumps(data))
    print(res.text)
    return json.loads(res.text)

#Cập nhật thông tin tất cả sản phẩm
def update_allcraw_product():
    products = get_all_product()
    print(products)
    for pd in products:
        idpd = pd['id']
        product_url = pd['product_url']
        data = crawNewBook(product_url)
        update_craw_product(idpd, data)
        
# update_allcraw_product()

# for index in cate_child_id:
#     product_list = get_data_product(str(index))
#     product_list_new = [insert('product', row.to_dict()) for index, row in product_list.iterrows() if not is_exists(check_url1.format('product', row['id']))]

