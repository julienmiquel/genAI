
import os

from langchain.chat_models import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel
from langchain.retrievers import GoogleVertexAISearchRetriever
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough

from langchain.tools import StructuredTool
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import VertexAI
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
import wikipedia
import vertexai

project_id = "ml-demo-384110"  # @param {type:"string"}
REGION = "europe-west1"  # @param {type:"string"}

TEXT_MODEL_VERSION =     "text-bison@001"


from langchain.tools import tool
from langchain.tools.base import ToolException
from langchain.tools import Tool

######## call back
# https://github.com/gilfernandes/chat_functions/blob/main/callbacks/agent_streamlit_writer.py

from typing import Optional
from langchain.callbacks.base import BaseCallbackHandler
from typing import Optional, Any
from uuid import UUID

from langchain.schema import (
    AgentAction,
    AgentFinish
)

import logging

def setup_log(module_name: str):
    logging.basicConfig(
        level='INFO', 
        format='%(asctime)s %(message)s', 
        datefmt='%m/%d/%Y %I:%M:%S %p',
        handlers=[
            logging.FileHandler("agent.log"),
            # logging.StreamHandler()
        ]
    )
    return logging.getLogger(module_name)

logger = setup_log("agent-logger")

class AgentCallbackHandler(BaseCallbackHandler):

    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run on agent action."""
        logger.info(f"on_agent_action tool: {action.tool}")
        logger.info(f"on_agent_action tool input: {action.tool_input}")
        logger.info(f"on_agent_action tool log: {action.log}")

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run on agent end."""
        logger.info(f"on_agent_finish re: {finish.return_values}")
        logger.info(f"on_agent_finish too logl: {finish.log}")


### call back        



@tool("current_date")
def current_date(query = None) -> str:
    '''
    Gets the current date (today), in the format YYYY-MM-DD
    '''
#    if param:
#        print(param)
    
    from datetime import datetime
    #import calendar 
    today = datetime.today()
    #calendar.day_name[today.weekday()]  #'Wednesday'
    
    todays_date = f"{today.strftime('%Y-%m-%d')}"
    #{calendar.day_name[today.weekday()]}"
    
    return todays_date




def _handle_error(error: ToolException) -> str:
    return (
        "The following errors occurred during tool execution:"
        + error.args[0]
        + "Please try another tool."
    )




# Text model instance integrated with langChain
llm = VertexAI(
    model_name=TEXT_MODEL_VERSION,
    max_output_tokens=1024,
    temperature=0.2,
    top_p=1.0,
    top_k=40,
    verbose=True,
)

# Text model instance integrated with langChain
llmTools = VertexAI(
    model_name=TEXT_MODEL_VERSION,
    max_output_tokens=1024,
    temperature=0.1,
    top_p=1.0,
    top_k=20,
    verbose=True,
)



wikipediaTools = load_tools(["wikipedia"], llm=llmTools)

#wikipediaTools[0].name = "Search fact inside wikipedia"

tools = []

tools.append(current_date)
tools.append(wikipediaTools[0])


agentWikipedia = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION ,
    verbose=True, 
)


#agentWikipedia.run("What's today's date?")
agentWikipedia.run("What are most important today news ? ",callbacks=[AgentCallbackHandler()])


