import requests
from bs4 import BeautifulSoup
from pprint import pprint

## 2. SELECT A WEBSITE AND MAKE A HTTP GET REQUEST

url = "http://ultra.md/search?search=casti+sony"

response = requests.get(url)

if (response.status_code != 200) :
    print("something is wrong")

## 3. SCRAPE THE PRODUCT NAME, PRICE, URL, MONTHLY_PAYMENT, AND IMAGE_URL

soup = BeautifulSoup(response.content, 'html.parser')

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
    # Product monthly payment
    product_info['monthly_payment'] = product.find('span',
                                                   class_='text-blue relative block text-sm font-normal dark:text-white').find(
        'span').text.strip()

    product_list.append(product_info)

## 4. SCRAPE THE PRODUCT LINK FOR ADDITIONAL DETAILS ADDITIONAL DETAILS
limited_list = product_list[0:2]
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

pprint(product_list)
