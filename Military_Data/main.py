import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import date, datetime, timedelta
import random
import pandas as pd, numpy as np


# In[16]:


# main url
main_url = "https://www.militarytoday.com"

# home url - to parse category names
home_url = "https://www.militarytoday.com/index.htm"

# category link example
category_url = 'https://www.militarytoday.com/helicopters.htm'

# item link example
item_url = "https://www.militarytoday.com/artillery/tam_vca.htm"


# # Define functions

# In[17]:


def get_response(url):
    cookies = { "cookie_name": "cookie_value" }
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'User-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
    response = requests.get(url, headers = headers, cookies = cookies)
    soup = BeautifulSoup(response.text, "html.parser")
    print(response)
    return soup


# In[34]:


# Home page level - parsing category links

def get_cat_links(home_link):
    soup = get_response(home_link)

    # create an empty set
    cat_set = set()

    # parse side table bar
    for i in soup.find("td", width ='9%', valign = "TOP").find_all('font'):
       # find link elements ("a")
        if i.find("a") != None:

            # get links (get("href"))
            cat_link = i.find("a").get("href")
            cat_name = i.text.replace("\n", "").replace("\t", "")
            # add to link set
            cat_set.add((cat_name, cat_link))

    cat_link_list = list(cat_set)[:-1]
    return cat_link_list


# In[41]:


# Category Level - parse sub-category headers and items
# parsing all item links and the sub-categories they belong to

def get_item_dict(cat_link):
    soup = get_response(cat_link)
    item_link_dict = {}
    # sub-category ("h2") and links ("a") parsing together
    all_items = soup.find("div", align = "CENTER").find_all(["h2", "a"])
    for element in all_items:

        # if element is header ("h2")
        if element.name == "h2":
            # make it dictionary key and assign to a list
            heading = element.text.replace("\n", "").replace("\t", "")
            item_link_dict[heading] = []

        # if element is link ("a")
        if element.name == "a":
            # append it to the list under related header (key)
            link = element.get("href")
            if link[-3:] == "htm":
                item_link_dict[heading].append(link)

    # result
    return item_link_dict


# In[65]:


# Item level - parsing item elements
# parsing all related elements from table

def item_parse(category, subcat, item_link):
    soup = get_response(item_link)
    militar_dict = {}

    militar_dict['Category'] = category
    militar_dict['Sub_category'] = subcat

    # Find 'Name' and 'Sub_text'
    name_font = soup.find('font', face="Arial", size=5)
    sub_text_font = soup.find('font', face="Arial", size=3)

    if name_font:
        militar_dict['Name'] = name_font.text
    else:
        militar_dict['Name'] = 'Name not found'

    if sub_text_font:
        militar_dict['Sub_text'] = sub_text_font.text.replace("\n", "")
    else:
        militar_dict['Sub_text'] = 'Sub_text not found'

    # Find table (td) info related to headers and data
    list_militar = soup.find_all('td', width="50%")

    for i in range(len(list_militar)):
        element = list_militar[i]
        if i % 2 == 0:
            header = element.text.strip()
            militar_dict[header] = 9
        elif i % 2 == 1:
            militar_dict[header] = element.text.strip()

    return militar_dict


# # Iterate

# In[80]:


parsed_item_list = []
parsed_item_dict = {}
category_list = get_cat_links(home_url)
for category in category_list:
    sub_cat_list = get_item_dict(category[1])
    for key in sub_cat_list:
        for item_link in sub_cat_list[key]:
            item_dict = item_parse(category[0], key, item_link)
            print(item_dict)
            parsed_item_list.append(item_dict)


# # Check the last item link and index

# In[84]:


value_to_find = item_link
# Iterate through the dictionary's key-value pairs
for key, value_list in sub_cat_list.items():
    if value_to_find in value_list:
        index = value_list.index(value_to_find)
        print(f'Value {value_to_find} found in {key}, index {index}')


# In[77]:


print(item_link)


# # Result

# In[85]:


pd.DataFrame(parsed_item_list)


# In[86]:


arm_data = pd.DataFrame(parsed_item_list)
arm_data.to_excel("arm_data.xlsx")
