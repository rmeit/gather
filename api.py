#%%
import os
import openai
import json
from langchain.chat_models import ChatOpenAI
# from langchain.memory import ConversationSummaryBufferMemory, ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts.prompt import PromptTemplate
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

api_key = #
openai.api_key = api_key
os.environ["OPENAI_API_KEY"] = api_key
model_list = openai.Model.list()
model = "gpt-3.5-turbo-0613"

class LLM():
    example_template = """
    You are an assistant to a human. The human is trying to do a task. You are trying to understand the task and help them achieve it.
    
    Current conversation:
    {history}
    Human: {input}
    AI:"""
    trivial_template = """
    {history}
    {input}
    """
    def __init__(self, model, template=example_template):
        self.model = model
        self.llm = ChatOpenAI(model=model)
        self.prompt = PromptTemplate(input_variables=["history", "input"], template=template)
        self.converation = ConversationChain(llm=self.llm, prompt=self.prompt, verbose=True)
    def __call__(self, input):
        return self.converation.predict(input=input)

class AggregatorInterface():
    def __init__(self, intro, option_str, outro):
        self.intro = intro
        self.options = option_str
        self.user_prefefences = {}
        self.outro = outro
    def add_user(self, user, preferences):
        self.user_prefefences[user] = preferences
    def get_user(self, user):
        return self.user_prefefences[user]
    def get_user_list(self):
        return self.user_prefefences.keys()
    def build_prompt(self):
        return f"""
        {self.intro}
        
        Here are the options:
        {self.options}
        
        Here are the user preferences:
        {str(self.user_prefefences)}
        
        {self.outro}
        
        your response should be json formatted as follows:
        {{
            'name': restaurant_name,
            'users': {{
                'username1': natural sounding response,
                ...
            }}
        }}
        
        """
    def __call__(self):
        raise NotImplementedError

class Aggregator(AggregatorInterface):
    def __init__(self, intro, option_str, outro, model=model):
        super().__init__(intro, option_str, outro)
        self.llm = LLM(model=model, template=LLM.trivial_template)
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
        f = open('restaurants.json')
        restaurant = [r for r in json.load(f) if r["name"] == name][0]
        wanted_keys = ['name', 'dollars', 'hours', 'rating', 'address', 'specialties', 'menu_link', 'img']
        return_dict = dict((k, restaurant[k]) for k in wanted_keys if k in restaurant)
        return_dict["users"] = info["users"]
        return return_dict
    def __call__(self):
        return print(self.llm(self.build_prompt()))
# %%

class FindDistances():
    def __init__(self, zipcode):
        self.main_address = zipcode
        self.geolocator = Nominatim(user_agent="greg")
        self.main_address_encoded = self.encode_zipcode(zipcode)
    def encode_address(self, address):
        p = self.geolocator.geocode(address)
        p = (p.latitude, p.longitude)
        if None in p:
            print("address not found")
            raise ValueError
        return p
    def encode_zipcode(self, zipcode):
        p = self.geolocator.geocode(query={'postalcode':zipcode, 'country': 'United States'}, addressdetails=True)
        p = (p.latitude, p.longitude)
        if None in p:
            print("address not found")
            raise ValueError
        return p
    def get_distance(self, a1, a2):
        return geodesic(self.encode_address(a1), self.encode_address(a2)).miles
    def __call__(self, address):
        return geodesic(self.main_address_encoded, self.encode_address(address)).miles
