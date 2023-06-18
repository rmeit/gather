#%%
import os
import openai
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
        prompt = self.intro
        prompt += "\nHere are the options:\n"
        prompt += self.options
        prompt += "\nHere are the user preferences:\n"
        prompt += str(self.user_prefefences) + "\n"
        prompt += self.outro
        return prompt
    def __call__(self):
        raise NotImplementedError

class Aggregator(AggregatorInterface):
    def __init__(self, intro, option_str, outro, model=model):
        super().__init__(intro, option_str, outro)
        self.llm = LLM(model=model, template=LLM.trivial_template)
    def __call__(self):
        return print(self.llm(self.build_prompt()))

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
