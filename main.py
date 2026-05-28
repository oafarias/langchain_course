from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")

numero_dias = 7
numero_criancas = 2
atividade = "praia"

modelo_prompt = PromptTemplate(
    template = """
    Crie um roteiro de viagens de {dias} dias, 
    para uma familia com {criancas} crianças, 
    que gostam de {atividade}.
    """
)

prompt = modelo_prompt.format(
    dias=numero_dias,
    criancas=numero_criancas,
    atividade=atividade
)

print(f"Prompt: \n{prompt}\n")

modelo = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.5,
    api_key=api_key
)

resposta = modelo.invoke(prompt)
print(resposta.content)