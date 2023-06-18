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

api_key = 0

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
    default_intro = """
        You are a helpful, informative, and concise AI assistant whose purpose is to help people be satisfied, especially when making group decisions or resolutions. You are very knowledgeable about nutrition and human allergies and are accommodating of such conditions.
        You will be given the restaurant preferences of different people. Your goal is to recommend a single  restaurant from the list below that will satisfy the preferences of all the people, based on the menu, description, and rating of each restaurant. Avoid low rated restaurants unless not other choices are available. If a person has allergies or cannot eat a certain food, make sure the restaurant is friendly to their needs (i.e. consider risk levels and also knowledge of the cuisine  of the restaurant), and specify when you are not sure whether a certain restaurant meets that criteria.
    """
    default_outro = """
        After you pick a single  restaurant by the guidelines above,  make a short human-like  reply to each user addressing how the restaurant satisfies their preferences, or if there are any concerns for their preferences.
    """
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
        # "specialties": "Inspired",
        # "menu_link": "https://www.yelp.com/biz_redir",
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
