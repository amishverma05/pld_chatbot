# pip install sentence-transformers
# python -m uvicorn api:app --reload
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import random
import time
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import os
import random
import logging

logging.basicConfig(
    level=logging.INFO,  # Show INFO and higher
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

import tomllib

with open("config.toml", "rb") as f:
    config = tomllib.load(f)

waiting_messages = [
    "Evaporating irrelevant data — condensing only what matters...",
    "Hold tight! Just ablating some knowledge from the right source.",
    "Target locked. Pulsing through dense research material...",
    "Synthesizing your solution — atom by atom.",
    "Filtering noise, amplifying the signal — your answer is forming.",
    "Gathering atoms of info… precision takes a second!",
    "Tuning parameters… the perfect reply is on its way.",
    "Just refining a few layers of thought…",
    "Your answer is almost deposited in the chamber.",
    "Reconstructing knowledge — coherence in progress.",
    "Bouncing off a few ideas… your insight is seconds away.",
    "We apologise for the delay, our bot was having a nap.",
    "Apologies for the wait! We’re just bribing the servers with coffee.",
    "Thanks for your patience!",
    "Your data is packed in a box… and the delivery guy will deliver it to you soon.",
    "Hang tight, we're getting that info for you...",
    "Just a moment — gathering the best response.",
    "Working on it… almost there!",
    "Give us a second to fetch the right answer.",
    "One sec — making sure it's accurate.",
    "Hold on… putting the pieces together.",
    "Processing your request — thanks for your patience.",
    "Looking that up… won't be long!",
    "Just checking the facts — back in a flash.",
    "Getting everything ready for you..."
]



class SemanticRAG:
    def __init__(self):
        genai.configure(api_key=os.getenv('gemini_api_key1'))  # This just configures the module
        self.model = genai.GenerativeModel(config["models"]["gemini_model"])
        self.pc = Pinecone(api_key=os.getenv('pinecone_api_key'))
        self.index = self.pc.Index(config["pinecone"]["index_name"])
        self.model_emb = SentenceTransformer(config["models"]["embedding_model"])

    def generate_embeddings(self, text):
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text

        em = self.model_emb.encode(texts)

        
        if isinstance(text, str):
            return em[0]


    def semantic_search2(self, query, k):
        ans=[]
        query_e=self.generate_embeddings(query)
        results = self.index.query(
            vector=query_e.tolist(),
            top_k=k,
            include_metadata=True
        )
        
        for match in results.matches:
            ans.append(match["metadata"]["text"])
        ans = list(set(ans))
        logger.info("Search for text done")
        return ans


    def genfirst(self, query, summ):
        logger.info("genfirst initiated")
        prompt = f"""
            You are given query. Find the most appropriate one or multiple paragraphs.
            Also tell a little about each paragraph by explicitly mentioning the asked parameter in query.

            Query: {query}


        """

        for i, para in enumerate(summ, 1):
            prompt += f"Paragraph {i}: {para}\n"

        retries = 3 
        success = False
        r=None
        while retries > 0 and not success:
            try:
                model = self.model
                r = model.generate_content(prompt)
                success = True
                
            except Exception as e:
                retries -= 1
                if retries > 0:
                    time.sleep(3)

        r=r.text
        logger.info("hint created in genfirst")
        return r


    def querygen(self, query):
        logger.info("querrygen initiated")

        prompt=f"""
        You are given a query. Return only the parameters in quotes.
        Return the answer in inverted comma.
        Example: "What is temperature of X thin films over KrF laser" then return "temperature X thin films KrF laser"

        Query: {query}

        """
        retries = 3 
        success = False
        while retries > 0 and not success:
            try:
                model = self.model
                r = model.generate_content(prompt)
                success = True
            except Exception as e:
                print(e)
                retries -= 1
                if retries > 0:
                    time.sleep(3)

        r=r.text
        logger.info("querry generated returned")
        return r


    def summarizer(self, query:str, k: int):
        # print("You're into semantic search 🔎...")
        logger.info("summaarizer function intiated")
        q=self.querygen(query)
        sim = self.semantic_search2(q,k)
        # print("Analysing the retrieved paragraphs 🕵🏻...")
        # print("...")
        
        summ = []
        for para in sim:

            retries = 3 
            success = False

            while retries > 0 and not success:
                try:
                    model = self.model
                    response = model.generate_content(f"""
                        Summarize the given text in only two lines (30 words).
                        Do not lose any information about parameters and materials, like temperature, wavelength, pressure, material name, substrate name, etc.
                        
                        Text:
                        {para}
                    """)

                    summ.append(response.text)
                    success = True
                except Exception as e:
                    retries -= 1
                    if retries > 0:
                        time.sleep(3)
        logger.info("summarised paras in 2 lines")         
        return summ

    def gensecond_semantic(self, query:str, k: int):
        logger.info("gensecond semantic funciton called")
        # logger.info("Thank you, We got your query✅...")
        # print("...")
        
        summ = self.summarizer(query, k)

        # print(summ)

        random_message = random.choice(waiting_messages)
        print(random_message)
        # print("...")

        r1 = self.genfirst(query, summ)

        # print(r1)
        # print("Generating your answer✍🏻...")

        
        
        prompt = f"""
            You have a query and the hint to the query about PLD (Pulsed Laser Deposition).
            1. Present to me it like you didn't get any hint and you're speaking it using your data. DON'T MENTION ANYTHING ABOUT PARAGRAPHS EXPLICITLY.
            2. Present every information. Dont miss anything, you have to present it in 30 to 150 words maximum, unless query asks to make it bigger.
            Query: 
            {query}
            Hint: 
            {r1}

        """

        print("--" * 60)
        retries = 3 
        success = False
        r=None
        while retries > 0 and not success:
            try:
                model = self.model
                r = model.generate_content(prompt)
                success = True
                
            except Exception as e:
                retries -= 1
                if retries > 0:
                    time.sleep(3)
        
        bot_response = r.text
        # print(r.text)
        logger.info("final result generated")
        return bot_response

# print(gensecond_semantic("What is the wavelength used in MgO thin films deposition",5))
    def chatbot_(self, user_input:str, k:int):
        
        logger.info("Received user Querry")
        r=self.gensecond_semantic(user_input, k)
        print(r)
        return r
        # print("Bot said 🤖: ", r)
    # chatbot_("What is the wavelength used in MgO thin films deposition",5)
    logger.info("summariser gensecond chatbot")