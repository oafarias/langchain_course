# Resumo: Métodos e Conceitos — LangChain & Python

## 1. Estrutura Básica de uma Cadeia
Uma cadeia no LangChain é fundamentada no conceito de **LCEL** (*LangChain Expression Language*) e composta por três elementos principais:
* **Prompt Template:** Define a estrutura da pergunta, contexto ou instrução.
* **Modelo LLM:** O motor que processa a entrada e gera a resposta textual.
* **Output Parser:** O componente que intercepta e formata a saída bruta do modelo em um tipo de dado útil (string, dicionário, JSON).

## 2. Prompt Template
Permite criar templates reutilizáveis com variáveis dinâmicas de forma padronizada.
* **Variáveis Dinâmicas:** Inseridas entre chaves `{variavel}` e alimentadas no `.invoke()`.
* **`partial_variables`:** Utilizado para injetar informações fixas ou instruções de formatação dinâmicas (como as vindas de um parser) sem precisar passá-las manualmente em toda execução.

## 3. Modelos LLM
Integração com provedores de IA (como a OpenAI através da classe `ChatOpenAI`). É o componente responsável por receber o prompt renderizado, processar os tokens e gerar a resposta preditiva com base nos parâmetros configurados (como `model` e `temperature`).

## 4. Output Parsers
Responsáveis por transformar a resposta do LLM em estruturas de dados tratáveis pelo Python:
* **`JsonOutputParser`:** Converte respostas textuais em objetos JSON estruturados (dicionários).
* **`StrOutputParser`:** Retorna a resposta limpa como uma string simples de texto puro.

## 5. Pydantic e BaseModel
Framework essencial para validação de tipos e garantia de contratos de dados em Python.
* **Estruturação:** Permite mapear classes estendendo `BaseModel` com atributos tipados.
* **Sintaxe Correta do `Field`:** Em versões recentes (Pydantic v2), descrições de campos devem utilizar obrigatoriamente o argumento nomeado `Field(description="...")` para evitar erros de inicialização de argumentos posicionais.

## 6. Concatenação de Cadeias (LCEL)
Uso do operador pipe (`|`) para criar uma esteira de execução declarativa.
* **Sintaxe:** <span style="color: red;">`cadeia = prompt | modelo | parser`</span>
* O LangChain gerencia o fluxo de dados por baixo dos panos, garantindo que a saída de um componente seja a entrada exata do próximo.

## 7. Cadeias Interligadas e Fluxos Complexos
Quando conectamos múltiplas cadeias onde a saída de uma vira a entrada da próxima, precisamos de atenção ao formato dos dados:
* **O Gargalo:** Parsers estruturados (como `JsonOutputParser`) cospem dicionários com múltiplas chaves. Se a cadeia seguinte esperar apenas uma variável específica, o fluxo quebrará com erros de inicialização (`TypeError`).
* **A Solução com Funções Anônimas:** Utilizamos expressões `lambda` no meio do encadeamento para filtrar e extrair estritamente o parâmetro necessário para o próximo prompt template.
* **Exemplo de Fluxo Filtrado:** `cadeia_final = cadeia_combinada | (lambda x: {"cidade": x["cidade"]}) | cadeia_3`


## 8. Evolução do Chatbot e Persistência de Contexto

Neste bloco do projeto "oafarias/langchain_course", o desenvolvimento do chatbot passou por três estágios evolutivos de gerenciamento de estado e arquitetura:

### Etapa 1: Chat Sem Memória (Stateless)
* **Conceito:** O modelo atua como um endpoint de requisição simples. Cada interação é isolada e tratada de forma independente; o LLM não retém o histórico das perguntas anteriores na mesma execução.
* **Status do Versionamento:** Apenas commitado (sem push).

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

modelo = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.5,
    api_key=api_key
)

lista_perguntas = [
    "Quero visitar um lugar no Brasil, famoso por praias e cultura. Pode sugerir?",
    "Qual a melhor época do ano para ir?"
]

for uma_pergunta in lista_perguntas:
    resposta = modelo.invoke(uma_pergunta)
    print("Usuário: ", uma_pergunta)
    print("IA: ", resposta.content, "\n")
```

### Etapa 2: Refatoração para LCEL (A Esteira Declarativa)

* **Conceito:** Introdução do `ChatPromptTemplate` e do `StrOutputParser` estruturados através do operador pipe (`|`). O código prepara a infraestrutura com placeholders para receber o histórico, embora a execução do loop ainda invoque o modelo de forma direta.
* **Status do Versionamento:** Apenas commitado (sem push).

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

modelo = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.5,
    api_key=api_key
)

prompt_sugestao = ChatPromptTemplate.from_messages(
    [
        ("system", "Você é um guia de viagem especializado em destinos brasileiros. Apresente-se como Sr. Passeios"),
        ("placeholder", "{historico}"),
        ("human", "{query}")
    ]
)

cadeia = prompt_sugestao | modelo | StrOutputParser()

lista_perguntas = [
    "Quero visitar um lugar no Brasil, famoso por praias e cultura. Pode sugerir?",
    "Qual a melhor época do ano para ir?"
]

for uma_pergunta in lista_perguntas:
    resposta = modelo.invoke(uma_pergunta)
    print("Usuário: ", uma_pergunta)
    print("IA: ", resposta.content, "\n")

```

### Etapa 3: Adição de Memória (Stateful)

* **Conceito:** Implementação real de estado utilizando `InMemoryChatMessageHistory` e `RunnableWithMessageHistory`. A cadeia passa a gerenciar sessões e injeta automaticamente o histórico de interações no placeholder `{historico}`, permitindo respostas contextuais consecutivas.
* **Status do Versionamento:** Push realizado (versão consolidada remota).

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

modelo = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.5,
    api_key=api_key
)

prompt_sugestao = ChatPromptTemplate.from_messages(
    [
        ("system", "Você é um guia de viagem especializado em destinos brasileiros. Apresente-se como Sr. Passeios"),
        ("placeholder", "{historico}"),
        ("human", "{query}")
    ]
)

cadeia = prompt_sugestao | modelo | StrOutputParser()

memoria = {}
sessao = "aula_langchain_alura"

def historico_por_sessao(sessao : str):
    if sessao not in memoria:
        memoria[sessao] = InMemoryChatMessageHistory()
    return memoria[sessao]

lista_perguntas = [
    "Quero visitar um lugar no Brasil, famoso por praias e cultura. Pode sugerir?",
    "Qual a melhor época do ano para ir?"
]

cadeia_com_memoria = RunnableWithMessageHistory(
    runnable=cadeia,
    get_session_history=historico_por_sessao,
    input_messages_key="query",
    history_messages_key="historico"
)

for uma_pergunta in lista_perguntas:
    resposta = cadeia_com_memoria.invoke(
        {
            "query" : uma_pergunta
        },
        config={"session_id":sessao}
    )
    print("Usuário: ", uma_pergunta)
    print("IA: ", resposta, "\n")

```
## 9. Orquestração de Assistentes Sem LangGraph

A orquestração permite criar sistemas que direcionam consultas para especialistas específicos com base no contexto da pergunta do usuário.

### Prompts Especializados

Cada consultor possui um prompt específico que define sua identidade e área de expertise:

```python
prompt_consultor_praia = ChatPromptTemplate.from_messages(
    [
        ("system", "Apresente-se como Sra Praia. Você é uma especialista em viagens com destinos para praia."),
        ("human", "{query}")
    ]
)

prompt_consultor_montanha = ChatPromptTemplate.from_messages(
    [
        ("system", "Apresente-se como Sr Montanha. Você é um especialista em viagens com destinos para montanhas e atividades radicais."),
        ("human", "{query}")
    ]
)
```

### Cadeias Especializadas

Cada consultor possui sua própria cadeia, permitindo respostas contextualizadas:

```python
cadeia_praia = prompt_consultor_praia | modelo | StrOutputParser()
cadeia_montanha = prompt_consultor_montanha | modelo | StrOutputParser()
```

### Roteador com Saída Estruturada

O roteador utiliza `TypedDict` para garantir que a decisão seja sempre um dos destinos válidos:

```python
from typing import Literal, TypedDict

class Rota(TypedDict):
    destino: Literal["praia", "montanha"]

prompt_roteador = ChatPromptTemplate.from_messages(
    [
        ("system", "Responda apenas com 'praia' ou 'montanha'"),
        ("human", "{query}")
    ]
)

roteador = prompt_roteador | modelo.with_structured_output(Rota)
```

### Função de Resposta Dinâmica

A função `responda` orquestra todo o fluxo, decidindo qual cadeia executar:

```python
def responda(pergunta: str):
    rota = roteador.invoke({"query": pergunta})["destino"]
    if rota == "praia":
        return cadeia_praia.invoke({"query": pergunta})
    return cadeia_montanha.invoke({"query": pergunta})
```

### Conceitos-Chave da Orquestração

* **Roteamento Inteligente:** O sistema analisa a pergunta e direciona para o especialista mais apropriado.
* **Prompts Especializados:** Cada consultor tem instruções específicas que definem seu comportamento e identidade.
* **Saída Estruturada:** O uso de `with_structured_output()` garante que o roteador sempre retorne um valor válido.
* **Decisão em Tempo de Execução:** A escolha da cadeia ocorre dinamicamente baseada na análise do roteador.