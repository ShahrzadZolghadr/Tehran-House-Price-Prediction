# -*- coding: utf-8 -*-
"""House_Web_Scraper.ipynb
"""
import requests
import re
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

def replace_page_number(input, newPageNumber):
    return input.replace('1', newPageNumber) 

def clean_text(text):
  text = re.sub(r'\s+','', text)
  return text

req_url = 'https://ihome.ir/sell-residential-apartment/th-tehran/?locations=iran.th.tehran&property_type=residential-apartment&paginate=30&page=1&is_sale=1&source=website&order_by=published_at&order_by_type=desc'
req = requests.get(req_url)

for i in range(1,160):
  r = requests.get(replace_page_number(req_url,str(i)))
  soup = BeautifulSoup(r.text , 'html.parser')

  area = soup.find_all("span", class_="sub-title")
  area_l = [clean_text(a.text) for a in area]
  main_data = soup.find_all("span" , class_= "property-detail__icons-item__value")
  main_data_l = [clean_text(a.text) for a in main_data]
  main_data_array = np.array(main_data_l).reshape(30,3)

  meters = main_data_array[:,0]
  years = main_data_array[:,1]
  rooms = main_data_array[:,2]

  sell_value = soup.find_all(class_= "sell-value")
  sell_value_l = [clean_text(a.text) for a in sell_value]

  links = soup.find_all("a", href= re.compile("details"))
  links_l = ['https://ihome.ir' + l['href'] for l in links]

  elevator, storage_area, parking_space, floor, position, terrace = [],[],[],[],[],[]
  look, units_per_floor, floors, WC_num, master_num, WC_type = [],[],[],[],[],[]
  for link in links_l:
    requ = requests.get(link)
    s =  BeautifulSoup(requ.text , 'html.parser')    
    features = s.find_all("div", class_ = 'properties__list')
    features_l = []
    for f in features:
      features_l.append(f.find_all("small", class_="title__item"))
      features_l.append(f.find_all("span", class_ = "number_item"))
    features_l = [re.sub(r'Loading...','', clean_text(fe[0].text)) for fe in features_l]
    elevator.append(features_l[1])
    storage_area.append(features_l[3])
    parking_space.append(features_l[5])
    floor.append(features_l[7])
    position.append(features_l[9])
    terrace.append(features_l[11])

    extra_l = []
    extra = s.find_all("div", class_ = 'properties__extra')
    for e in extra:
      extra_l.append(e.find_all("small", class_="title__item"))
      extra_l.append(e.find_all("span", class_ = "number_item"))
    extra_l = [re.sub(r'Loading...','', clean_text(ex[0].text)) for ex in extra_l]
    look.append(extra_l[extra_l.index("??????")+1]) if extra_l.count("??????")!=0 else look.append("nan")
    units_per_floor.append(extra_l[extra_l.index("??????????????????????????????")+1]) if extra_l.count("??????????????????????????????")!=0 else units_per_floor.append("nan")
    floors.append(extra_l[extra_l.index("????????????????????")+1]) if extra_l.count("????????????????????")!=0 else floors.append("nan")
    WC_num.append(extra_l[extra_l.index("??????????????????????????????????")+1]) if extra_l.count("??????????????????????????????????")!=0 else WC_num.append("nan")
    master_num.append(extra_l[extra_l.index("????????????????")+1]) if extra_l.count("????????????????")!=0 else master_num.append("nan")
    WC_type.append(extra_l[extra_l.index("??????????????????????????????")+1]) if extra_l.count("??????????????????????????????")!=0 else WC_type.append("nan")

  list_of_tuples = list(zip(area_l, meters, years, rooms, elevator, storage_area, parking_space, floor, position, terrace, 
                            look, units_per_floor, floors, WC_num, master_num, WC_type, sell_value_l))
  
  cls = ['area', 'meters', 'years', 'rooms', 'elevator', 'storage_area', 'parking_space', 'floor', 'position', 'terrace', 
                        'look', 'units_per_floor', 'floors', 'WC_num', 'master_num', 'WC_type', 'sell_value']

  if i == 1:
    Houses_df = pd.DataFrame(list_of_tuples, columns = cls)
  else:
    df = pd.DataFrame(list_of_tuples, columns = cls)
    Houses_df = Houses_df.append(df , ignore_index = True)
