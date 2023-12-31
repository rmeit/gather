import requests
from bs4 import BeautifulSoup
import json
import os

headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Google Chrome\";v=\"90\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Cookie":'bse=97e259dfdea54d7abcb6cde8138bd6e2; hl=en_US; wdi=2|06E0C1E3B36E3EC1|0x1.9233cfe75d1c4p+30|1a845ae4cc194d62; _gid=GA1.2.1941446017.1686959102; _gcl_au=1.1.1406439604.1686959102; qntcst=D; _scid=5f18ddbc-3e64-4065-b1ab-e9f6e0bc8955; _tt_enable_cookie=1; _ttp=9DsW5MEsr8A6dNCTuNobh3d7Lif; _sctr=1%7C1686898800000; __adroll_fpc=ed0bc8cef3a423d9c8ac36294edfe27e-1686959105550; _fbp=fb.1.1686959106513.399004745; _ga_4DDTFPQZN7=GS1.1.1687038871.1.1.1687038876.0.0.0; _ga=GA1.2.06E0C1E3B36E3EC1; g_state={"i_l":0}; zss=nWO3adRbGBTLFPluemD1SWSixS2OZA; recentlocations=; hsfd=0; rsp=%7B%22date%22%3A%222023-06-17%22%2C%22time%22%3A%221900%22%2C%22partySize%22%3A2%7D; location=%7B%22provenance%22%3A+%22YELP_GEOCODING_ENGINE%22%2C+%22place_id%22%3A+%221747%22%2C+%22parent_id%22%3A+%22fyLxPHY_YaolQevqkTRTUQ%22%2C+%22location_type%22%3A+%22locality%22%2C+%22longitude%22%3A+-122.27598689807789%2C+%22min_latitude%22%3A+37.845867%2C+%22address1%22%3A+%22%22%2C+%22min_longitude%22%3A+-122.325193%2C+%22zip%22%3A+%22%22%2C+%22display%22%3A+%22Berkeley%2C+CA%22%2C+%22latitude%22%3A+37.8723101046192%2C+%22unformatted%22%3A+%22Berkeley%2C+CA%22%2C+%22city%22%3A+%22Berkeley%22%2C+%22county%22%3A+%22Alameda+County%22%2C+%22accuracy%22%3A+4%2C+%22country%22%3A+%22US%22%2C+%22max_longitude%22%3A+-122.234185%2C+%22address2%22%3A+%22%22%2C+%22max_latitude%22%3A+37.905824%2C+%22state%22%3A+%22CA%22%2C+%22address3%22%3A+%22%22%2C+%22borough%22%3A+%22%22%2C+%22isGoogleHood%22%3A+false%2C+%22language%22%3A+null%2C+%22neighborhood%22%3A+%22%22%2C+%22polygons%22%3A+null%2C+%22usingDefaultZip%22%3A+false%2C+%22confident%22%3A+null%7D; adc=EAvuVMdAwC0FRRFY9iVovQ%3AB2atP7uF4dEpacCwFhEADw%3A1687044547; xcj=1|xWeTMw25aNNoL3sJmauDhD5q-lUqoHp62_zXXRMmfR8; _scid_r=5f18ddbc-3e64-4065-b1ab-e9f6e0bc8955; _gat_www=1; _gat_global=1; _ga_K9Z2ZEVC8C=GS1.2.1687038831.2.1.1687044682.0.0.0; _uetsid=d05b81000c9f11ee88cd27ed9a45a6f3; _uetvid=40e60c00581311ed9e32653ef9c7453f; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Jun+17+2023+16%3A31%3A22+GMT-0700+(Pacific+Daylight+Time)&version=202304.1.0&browserGpcFlag=0&isIABGlobal=false&consentId=consumer-l4klc71rvN_f5eLD6E6bIQ&hosts=&interactionCount=1&landingPath=NotLandingPage&groups=BG82%3A1%2CC0003%3A1%2CC0002%3A1%2CC0001%3A1%2CC0004%3A1&AwaitingReconsent=false; __ar_v4=MXKM3BBNB5GURITSUD7B5B%3A20230616%3A2%7CBHPKS4B4ONEJJMGH4QCJZR%3A20230616%3A19%7CQB5JPFIKRZDSBOZSULG4YB%3A20230616%3A19%7C7YX6SJQ4RZAMPB6LZ7CHFF%3A20230616%3A8%7CEJF25UGRZJG7ZAP6TC6HPR%3A20230617%3A2%7CPQBTU2EVFFH7XPLFPIQ7B2%3A20230617%3A5%7COQFTDIJLVFFHLMQ2H2UVHV%3A20230617%3A2',
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "X-Amzn-Trace-Id": "Root=1-609b3347-59f1ba2d65f6c2ad14aac0c3"
}

def scrape_berkeley_restaurants():
    url = 'https://www.yelp.com/search?find_desc=&find_loc=Berkeley%2C+CA'
    # there are 230 or so
    for i in range(24):
        request_url = url
        if i > 0:
            request_url = url+"&start="+ str(10*i)
        r = requests.get(request_url, allow_redirects = True, headers = headers)
        html = r.content

        soup = BeautifulSoup(html,'html.parser')
        restaurants = soup.find_all('div', {"data-testid":"serp-ia-card"})

        restaurant_data = []

        for restaurant in restaurants:
            link = restaurant.find('a', {"class":"css-19v1rkv"})
            restaurant_link = link['href']


            if "campaign_id" in restaurant_link:
                start = restaurant_link.find("www.yelp.com%2Fbiz%2F")
                end = restaurant_link.find("&request_id")
                restaurant_link = "/biz/"+restaurant_link[start+21:end]

            restaurant_link = "https://www.yelp.com"+ restaurant_link
            r = requests.get(restaurant_link, allow_redirects = True, headers = headers)
            content = str(r.content)

            start = content.find('property="og:description" content="')
            sub_content = content[start+35:]
            end = sub_content.find('">')
            specialties = sub_content[:end]

            start = content.find('role="img" aria-label="')
            sub_content = content[start+23:]
            end = sub_content.find('">')
            rating = sub_content[:end]
            rating = rating[:-12]

            start = content.find('" css-qyp8bo" data-font-weight="semibold">')
            sub_content = content[start+42:]
            end = sub_content.find('</p>')
            address = sub_content[:end]

            restaurant_html = BeautifulSoup(content,'html.parser')

            name = restaurant_html.find('h1')
            if name:
                name = name.text

            dollars = restaurant_html.find('span',{"class":"css-1fdy0l5"})
            if dollars:
                if "$" in dollars:
                    dollars = dollars.text
                else:
                    dollars = ""
            else:
                dollars = ""

            maybe_menus = restaurant_html.find_all('a',{"class":"css-11i4m5w", "data-button":"true"})
            menu = ""
            if maybe_menus:
                for maybe_menu in maybe_menus:
                    if "yelp.com/biz_redir" in maybe_menu["href"]:
                        menu = maybe_menu['href']
            if menu == "":
                menu = restaurant_link

            hours = restaurant_html.find('span',{"class":"display--inline__09f24__c6N_k margin-l1__09f24__m8GL9 border-color--default__09f24__NPAKY"})
            if hours:
                hours = hours.text

            img = restaurant_html.find('img',{"class":"photo-header-media-image__09f24__A1WR_"})
            if img:
                img = img['src']

            popular_dishes = [dish.text for dish in restaurant_html.find_all('p',{"class":"css-nyjpex"})]

            address = restaurant_html.find('p',{"class":"css-qyp8bo", "data-font-weight":"semibold"})
            if address:
                address = address.text

            restaurant_json = {}
            restaurant_json["name"] = name
            restaurant_json["dollars"] = dollars
            restaurant_json["hours"] = hours
            restaurant_json["rating"] = rating
            restaurant_json["popular_dishes"] = popular_dishes
            restaurant_json["address"] = address
            restaurant_json["specialties"] = specialties
            restaurant_json["menu_link"] = menu
            restaurant_json["img"] = img
            restaurant_data.append(restaurant_json)
        print(i)
        write_file = open("more_restaurants_"+str(i)+".json", 'w')
        write_file.write(json.dumps(restaurant_data))
        write_file.close()

    all_data = []
    for i in range(24):
        f = open('more_restaurants_'+str(i)+'.json')
        data = json.load(f)
        all_data.extend(data)
        os.remove('more_restaurants_'+str(i)+'.json')

    write_file = open("more_restaurants_.json", 'w')
    write_file.write(json.dumps(all_data))
    write_file.close()

    # for the static database we need to manually clean a little bit
    # use an actual API for the future

def parse_info(str):
    # The output takes this format
    # {
    # "name": "Lavender Bakery and Cafe",
    # "dollars": "$",
    # "hours": "8:00 AM - 8:00 PM",
    # "rating": "4.5",
    # "address": "1820 Solano Ave Berkeley, CA 94707",
    # "specialties": "Inspired by the desire to bring authentic European recipes to Berkeley, Lavender Bakery and Cafe began serving friends, neighbors and customers the best in Bay Area baked goods in October 2018.Famous for Burnt Almond, The Lavender Bakery has been bringing the finest authentic European inspired cakes and baked goods to the bay area. With two sister bakeries located in south bay silicon valley, Lavender Bakery serves a variety of cakes, cupcakes, pies, desserts, cookies, pastries and many seasonal and occasional items. Established in 2018.  Famous for Burnt Almond, The Lavender Bakery has been bringing the finest authentic European inspired cakes and baked goods to the bay area. With two sister bakeries located in south bay silicon valley, Lavender Bakery serves a variety of cakes, cupcakes, pies, desserts, cookies, pastries and many seasonal and occasional items.",
    # "menu_link": "https://www.yelp.com/biz_redir?cachebuster=1687069122&s=49b13b9a5fd9fbbca9956e08fad2393d7d3fa5a9e7383be45481bfd8b4384711&src_bizid=lQYwz5KWxdiXjRttkAI6AQ&url=https%3A%2F%2Fwww.lavenderbakeries.com%2Fs%2Fsplash&website_link_type=menu",
    # "img": "https://s3-media0.fl.yelpcdn.com/bphoto/LDYjVd24saj82ixl4mTaFw/l.jpg"
    # "users" :
    #   {
    #       "username0" : "explanation0",
    #       "username1" : "explanation1"
    #   }
    # }
    info = json.loads(str)
    name = info["name"]
    print(name)
    f = open('restaurants.json')
    restaurants = json.load(f)
    restaurant = [r for r in restaurants if r["name"] == name ][0]
    wanted_keys = ['name', 'hours', 'address', 'dollars', 'rating', 'specialties', 'menu_link', 'img']
    return_dict = dict((k, restaurant[k]) for k in wanted_keys if k in restaurant)
    return_dict["users"] = info["users"]
    return return_dict


