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

with open("openkey.txt", 'r') as f:
    api_key = f.read()

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
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.prompt = PromptTemplate(input_variables=["history", "input"], template=template)
        self.converation = ConversationChain(llm=self.llm, prompt=self.prompt, verbose=True)
    def __call__(self, input):
        return self.converation.predict(input=input)

class AggregatorInterface():
    def __init__(self, intro, option_str, outro, user_preferences={}):
        self.intro = intro
        self.options = option_str
        self.user_preferences = user_preferences
        self.outro = outro
    def add_user(self, user, preferences):
        self.user_preferences[user] = preferences
    def get_user(self, user):
        return self.user_preferences[user]
    def get_user_list(self):
        return self.user_preferences.keys()
    def build_prompt(self):

        return f"""
        {self.intro}
        
        Here are the options:
        {self.options}
        
        Here are the user preferences:
        {str(self.user_preferences)}
        
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

old_outro = """
        After you pick a single restaurant by the guidelines above, make a short human-like reply to each user addressing how the restaurant satisfies their preferences, or if there are any concerns for their preferences. The content of the response must be truthful and reference specific menu items, while ensuring that the restaurant you pick has all the menu items you list in your response. Also, the phrasing should make every user feel satisfied with the restaurant decision.  Make sure the same restaurant is recommended to each user. Note that each user will only see the response directed to them, and not any others.
"""
class Aggregator(AggregatorInterface):
    default_intro = """
        You are a helpful, truthful, informative, and concise AI assistant whose purpose is to help people be satisfied, especially when making group decisions or resolutions. You are very knowledgeable about nutrition and human allergies and are accommodating of such conditions.
        You will be given the restaurant preferences of different people. Your goal is to recommend a single restaurant from the list below that will maximize the satisfaction of the preferences of the users, based on the menu, description, and rating of each restaurant. Avoid low rated restaurants unless no other choices are available. If a user has allergies or cannot eat a certain food, make sure the restaurant is friendly to their needs (i.e. consider risk levels and also knowledge of the cuisine  of the restaurant), and specify when you are not sure whether a certain restaurant meets that criteria.
        You should carefully consider each item on the menus and think about what possible ingredients might go into each dish when considering preferences of users, and whether the ingredients fulfill those preferences. Balance the importance of preferences of all users to be equal apart from dietary restrictions, and apply gain control.
    """
    default_outro = """
        Once you have picked a single restaurant by the guidelines above, pretend you are the owner of that restaurant. Pretend that you are sitting down with each of the users and explaining why they should eat at your restaurant. Make sure address their preferences and mention specific menu items that your chefs will create.
    """

    def __init__(self, intro, option_str, outro, user_preferences={}, model=model):
        super().__init__(intro, option_str, outro, user_preferences)
        self.model = model
        self.llm = None
        self.reset_llm()
    def reset_llm(self):
        del self.llm
        self.llm = LLM(model=self.model, template=LLM.trivial_template)
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
        print(self.llm(self.build_prompt()))
        self.reset_llm()

class StepAggregator(AggregatorInterface):
    default_intro = """
        You are a helpful, truthful, informative, and concise AI assistant whose purpose is to help people be satisfied, especially when making group decisions or resolutions. You are very knowledgeable about nutrition and human allergies and are accommodating of such conditions.
        You will be given the restaurant preferences of different people. Your goal is to recommend a single restaurant from the list below that will maximize the satisfaction of the preferences of the users, based on the menu, description, and rating of each restaurant. Avoid low rated restaurants unless not other choices are available. If a user has allergies or cannot eat a certain food, make sure the restaurant is friendly to their needs (i.e. consider risk levels and also knowledge of the cuisine  of the restaurant), and specify when you are not sure whether a certain restaurant meets that criteria.
        You should carefully consider each item on the menus and think about what possible ingredients might go into each dish when considering preferences of users, and whether the ingredients fulfill those preferences. Balance the importance of preferences of all users to be equal apart from dietary restrictions, and don't be swayed by one user's opinion.
    """
    default_outro = """
        output the name of the restaurant you pick in the following format {'name': restaurant_name}
    """

    def __init__(self, intro, option_str, outro, user_preferences={}, model=model):
        super().__init__(intro, option_str, outro, user_preferences)
        self.model = model
        self.llm = None
        self.reset_llm()
    def reset_llm(self):
        del self.llm
        self.llm = LLM(model=self.model, template=LLM.trivial_template)
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
        print(self.llm(self.build_prompt_preference()))
        self.reset_llm()
    def build_prompt_restaurant(self):

        return f"""
        {self.intro}

        Here are the options:
        {self.options}

        Here are the user preferences:
        {str(self.user_preferences)}

        {self.outro}
        """
    def build_prompt_preference(self):
            return f"""
            You are a helpful, truthful, informative, and concise AI assistant whose purpose is to help people be satisfied, especially when making group decisions or resolutions. You are very knowledgeable about nutrition and human allergies and are accommodating of such conditions.
            You will be given the restaurant preferences of different people. Your goal is to convince each user that the restaurant you have chosen will maximize the satisfaction of the preferences of the users. Your response will be based on the menu, description, and rating of each restaurant. If a user has allergies or cannot eat a certain food, make sure the restaurant is friendly to their needs (i.e. consider risk levels and also knowledge of the cuisine  of the restaurant), and specify when you are not sure whether the restaurant meets that criteria.

            Here is the restaurant you are reccomending to each user:
            {{
                "name" : "Eureka!",
                "dollars" : "$$",
                "hours" : "11:00 AM - 1:00 AM ",
                "rating" : "4",
                "popular_dishes" : [
                "Cowboy",
                "Fresno Fig",
                "Jalapeno Egg",
                "Steak Salad"
                ],
                "address" : "2068 Center St Berkeley, CA 94704",
                "specialties" : "Specialties: Eureka! features an elevated collection of all-American fare paired with local craft beers, small-batch whiskeys, and cocktails making it the perfect place for for the local community to dine, drink and socialize. Established in 2009.  Eureka! is defined as expressing delight on finding, discovering or solving something... burger connoisseurs are discovering a better burger experience and Eureka! has elevated it to an art form requiring grace, finesse and sophistication. Acting with care ensures that efficiency never becomes haste and quality never suffers for convenience. Through thoughtful presentation of ourselves and our food, we show respect for our ingredients, our buildings, our guests and our colleagues."
            }}

            Here are the user preferences:
            {str(self.user_preferences)}

            your response should be json formatted as follows:
            {{
                'name': restaurant_name,
                'users': {{
                    'username1': natural sounding response,
                    ...
                }}
            }}

            """

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


options = """

 {
    "name" : "Eureka!",
    "dollars" : "$$",
    "hours" : "11:00 AM - 1:00 AM ",
    "rating" : "4",
    "popular_dishes" : [
      "Cowboy",
      "Fresno Fig",
      "Jalapeno Egg",
      "Steak Salad"
    ],
    "address" : "2068 Center St Berkeley, CA 94704",
    "specialties" : "Specialties: Eureka! features an elevated collection of all-American fare paired with local craft beers, small-batch whiskeys, and cocktails making it the perfect place for for the local community to dine, drink and socialize. Established in 2009.  Eureka! is defined as expressing delight on finding, discovering or solving something... burger connoisseurs are discovering a better burger experience and Eureka! has elevated it to an art form requiring grace, finesse and sophistication. Acting with care ensures that efficiency never becomes haste and quality never suffers for convenience. Through thoughtful presentation of ourselves and our food, we show respect for our ingredients, our buildings, our guests and our colleagues."
  },
  {
    "name" : "Angeline's Louisiana Kitchen",
    "dollars" : "$$",
    "hours" : "10:00 AM - 9:00 PM",
    "rating" : "4",
    "popular_dishes" : [
      "Jambalaya",
      "Buttermilk Fried Chicken",
      "Fried Catfish",
      "Shrimp Creole",
      "Crawfish Etouffee",
      "Cajun Mixed Grill",
      "Baby Back Ribs",
      "Angeline's Creole-style BBQ Shrimp",
      "Red Beans and Rice",
      "Wild Mushroom Jambalaya",
      "Voo Doo Shrimp"
    ],
    "address" : "2261 Shattuck Ave Berkeley, CA 94704",
    "specialties" : "Specialties: Angeline's brings the flavor and atmosphere of a New Orleans neighborhood restaurant to downtown Berkeley, with great music, libations and the classic dishes invented in the Crescent City's greatest kitchens. We offer down-home classics like Gumbo, Jambalaya, Fried Catfish, or our Buttermilk Fried Chicken. For dessert, try our Bananas Foster Bread Pudding or our signature warm Beignets with chicory coffee. Whatever you try, you'll leave happy. Established in 2006.  Angeline's began as the dream of founder Robert Volberg as a way to bring southern hospitality and the delicious flavors of New Orleans to the bay area.  Inspired by the neighborhood jambalaya joints he had visited on a trip to the Big Easy six months before Katrina, Robert was looking for a location for his new restaurant when he struck up a conversation with a man in chef's pants in Oakland's Rockridge district.  The man was Chef Brandon Dubea from Baton Rouge, LA.  After working to develop an outstanding menu and create a delightful atmosphere, Angeline's opened quietly and gained popularity slowly after opening.  After reviews in the East Bay Express, SF Chronicle, Diablo Magazine and many others which hailed Chef Dubea's cuisine as 'authentic' and dishes as having 'real character', Angeline's was featured on an episode of 'Check Please, Bay Area'.  As word spread about the restaurant, Tempe Minaga completed the team as co-owner in mid 2008 to improve service and operations."
  },
{
    "name" : "Fish & Bird Sousaku Izakaya",
    "dollars" : “”
    "hours" : "4:30 PM - 9:30 PM",
    "rating" : "4",
    "popular_dishes" : [
      "Chicken Karaage",
      "Chicken Katsu",
      "Sea Beans & Corn Tempura",
      "Chicken Katsu Curry",
      "Agedashi Tofu",
      "Soft Tofu",
      "Green Beans Fritters W/ Curry Sansho Salt",
      "Deluxe Sashimi Moriawase",
      "Seasonal Salad"
    ],
    "address" : "2451 Shattuck Ave Berkeley, CA 94704",
    "specialties" : "Specialties: Fish & Bird is a unique izakaya style restaurant and bar, specializing in modern Japanese cuisine. The modern, sophisticated interpretation of traditional dishes is a reflection of the current trends in Japan."
  }


"""
# %%
