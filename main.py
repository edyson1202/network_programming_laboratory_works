import ssl
import functools
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re

import socket

def dict_to_xml(d, root_element="root"):
    # Start with the root element
    xml_string = f'<{root_element}>'

    for key, value in d.items():
        if isinstance(value, dict):
            # Recursively convert dictionaries
            xml_string += dict_to_xml(value, key)
        elif isinstance(value, list):
            # Handle lists by creating a separate element for each item
            for item in value:
                xml_string += f'<{key}>'
                if isinstance(item, dict):
                    xml_string += dict_to_xml(item, key)
                else:
                    xml_string += str(item)
                xml_string += f'</{key}>'
        else:
            # Convert other types to string
            xml_string += f'<{key}>{str(value)}</{key}>'

    xml_string += f'</{root_element}>'
    return xml_string

def dict_to_json(d):
    # Handle the empty dictionary case
    if not d:
        return '{}'

    items = []

    for key, value in d.items():
        # Convert the key to a JSON-compatible string
        key_str = f'"{key}"'

        # Convert the value based on its type
        if isinstance(value, str):
            value_str = f'"{value}"'
        elif isinstance(value, (int, float, bool)):
            value_str = str(value).lower() if isinstance(value, bool) else str(value)
        elif value is None:
            value_str = 'null'
        elif isinstance(value, dict):
            value_str = dict_to_json(value)  # Recursively convert dictionaries
        elif isinstance(value, list):
            # Handle lists by converting each item
            list_items = ', '.join(dict_to_json({i: v}) for i, v in enumerate(value))
            value_str = f'[{list_items}]'
        else:
            raise TypeError(f'Unsupported type: {type(value)}')

        # Combine the key and value into a JSON string format
        items.append(f'{key_str}: {value_str}')

    # Join all items into a JSON object string
    return '{' + ', '.join(items) + '}'

def http_get(host, path):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    context = ssl.create_default_context()

    sock = context.wrap_socket(sock, server_hostname=host)

    sock.connect((host, 443))

    # Prepare the HTTP GET request
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

    # Send the request
    sock.sendall(request.encode())

    # Receive the response
    response = b""
    while True:
        part = sock.recv(4096)
        if not part:
            break
        response += part

    # Close the socket
    sock.close()

    # Return the response
    response_text = response.decode()

    headers, body = response_text.split("\r\n\r\n", 1)
    print(headers)
    return body


def mdl_to_eur(data_dict) :
    exchange_rate = 1 / 20

    data_dict['price'] = float(data_dict['price']) * exchange_rate
    data_dict['price'] = str(data_dict['price']) + ' EUR'

    return data_dict

def filter_in_price_range(data_dict) :
    min = 100
    max = 200

    price = float(re.sub(r'[A-Za-z]', '', data_dict['price']).replace(' ', ''))
    print(price)
    if price > min and price < max :
        return data_dict

## 2. SELECT A WEBSITE AND MAKE A HTTP GET REQUEST

path = "/search?search=casti+sony"
host = "ultra.md"
url = "http://ultra.md/search?search=casti+sony"

soup = ""
useSocket = True;
if useSocket :
    response = http_get(host, path)
    soup = BeautifulSoup(response, 'html.parser')
else :
    response = requests.get(url)
    if (response.status_code != 200):
        print("something is wrong")

    soup = BeautifulSoup(response.content, 'html.parser')


## 3. SCRAPE THE PRODUCT NAME, PRICE, URL, MONTHLY_PAYMENT, AND IMAGE_URL



product_list = []

for product in soup.find_all('div', class_='product-block product-block-card hover:shadow-product border h-full border-gray-100 rounded-bg bg-white p-3 transition-shadow duration-200 dark:border-gray-700 dark:bg-gray-900') :
    product_info = {}

    # Product link
    product_info['url'] = product.find('a', class_='relative flex items-center justify-center lazypreload')['href']

    # Product title
    product_info['title'] = product.find('a',
                                         class_='product-text pt-4 font-semibold text-gray-900 transition duration-200 hover:text-red-500 dark:text-white sm:text-sm').text.strip()
    # Product image URL
    product_info['image_url'] = product.find('img', class_='mb-4 h-48 w-48 object-contain lg:h-64 lg:w-64')['src']

    # Product price
    product_info['price'] = product.find('span', class_='text-blue text-xl font-bold dark:text-white').text.strip()
    product_info['price'] = product_info['price'].replace(' ', '').replace('\n', '')
    product_info['price'] = ''.join(filter(str.isdigit, product_info['price']))
    # Product monthly payment
    montly_payment = product.find('span',
                                                   class_='text-blue relative block text-sm font-normal dark:text-white').find('span').text.strip()
    product_info['monthly_payment'] = montly_payment if montly_payment.isdigit() else '-1 ' + montly_payment

    product_list.append(product_info)

## 4. SCRAPE THE PRODUCT LINK FOR ADDITIONAL DETAILS ADDITIONAL DETAILS
limited_list = product_list[0:1]
for product_info in limited_list :
    url = product_info['url']

    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract connectivity information
    connectivity_info = {}

    # Find all table rows
    rows = soup.find_all('tr')

    for row in rows:
        # Get the type of connection
        connection_type = row.find('td').find('span').get_text(strip=True)
        # Get the corresponding value
        connection_value = row.find_all('td')[1].get_text(strip=True)

        # Add to the dictionary
        connectivity_info[connection_type] = connection_value

    product_info['connectivity_info'] = connectivity_info

## 6. MAP PRICES FROM MDL TO EUR, FILTER IN A PRICE RANGE, AND USE REDUCE TO SUM UP THE PRICES OF FILTERED PRODUCTS

product_list = list(map(mdl_to_eur, product_list))

product_list = list(filter(filter_in_price_range, product_list))


price_list = []

for product in product_list :
    price_list.append(float(product['price'].replace(' EUR', '')))

print(price_list)

# Use reduce to compute the product of list elements
sum = functools.reduce(lambda x, y: x + y, price_list)
print("Sum of list prices:", sum)

sum_timestamp = {}

sum_timestamp['prices_sum'] = sum
sum_timestamp['utc_timestamp'] = str(datetime.utcnow())

product_list.append(sum_timestamp)

content = {}
content['content'] = product_list

json_string = dict_to_json(content)
xml_string = dict_to_xml(content)

print(json_string)
print(xml_string)

#pprint(content)






