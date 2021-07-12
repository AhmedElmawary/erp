import random
from typing import Dict
from app.settings import BASE_DIR, HELPERS_RELATIVE_PATH
import os, json
from datetime import datetime , timedelta

SUPPLIER  = {
'name': 'ahmed',
'phone': '+20113215564',
'gender': 1,
'address': 'asdasd',
'city': 'Cairo',
'country': 'EG',
'cash': 1000,
}

STATUS = {
    'name':'Pending'
}

SUPPLIER_TRANSACTIONS = {
    'amount':5000,
    'supplier':1,
    'currency': 1
}

def _names_path() -> str:
    helpers = os.path.join(BASE_DIR, HELPERS_RELATIVE_PATH)
    return f'{helpers}/NAMES.json'

def _get_names_json():
    with open(_names_path(), 'r') as json_file:
        return json_file.read()


def json_names_to_dic(limit=-1) -> Dict: 
    return json.loads(_get_names_json())['names'][:limit]

def numbers_generator(loop_no):
    numbers_set = set()
    numbers = [1,2,3,4,5,6,7,8,9,0]
    
    for time in range(loop_no):
            number = get_value_by_index(time, numbers)
            
            number+=1
   
            number_row = [ f'{ number * 4}' , f'{number * 2 * number *12}' , f'{number *21 + number *34}',f'{number *31+number * 14}']
   
            random.shuffle(number_row)
   
            add_to_set(number_row, numbers_set)
            
    return numbers_set


def add_to_set(value: str, values: set):
    try:
        values.remove(value)
        value =  datetime.now().timestamp()
    except:
        value = ''.join(value)
    finally:
        values.add(value)
    
def get_value_by_index(index, values):
    if index >= len(values):
        index=0
    return values[index]

def remove_from_set(index, values :set()):
    if index >= len(values):
        index=0
    return values.pop()


def generate_new_number():
    return numbers_generator(1).pop()


def validate_num(number, numbers):
    return (number in numbers)


def generate_phone(name):
    phone =  list(name)
    phone += str(datetime.now().time())
    random.shuffle(phone)
    
    return ''.join(phone)[:14]
