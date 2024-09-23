import openai
from fastapi import HTTPException
import os
from dotenv import load_dotenv
from typing import List 

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_tutor_response(user_message: str, conversation_history: list, knowledge_base: list):
    try:
        # Prepare the conversation history
        messages = [
            {"role": "system", "content": "You are a knowledgeable tutor specializing in software testing, APIs, and Azure DevOps."}
        ]
        
        # Add conversation history
        for msg in conversation_history:
            role = "user" if msg.is_user else "assistant"
            messages.append({"role": role, "content": msg.content})
        
        # Add relevant knowledge base items
        if knowledge_base:
            knowledge_content = "\n".join([item.content for item in knowledge_base])
            messages.append({"role": "system", "content": f"Here's some relevant information: {knowledge_content}"})
        
        # Add the current user message
        messages.append({"role": "user", "content": user_message})
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        
        return response.choices[0].message['content'].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

async def generate_summary(messages: List[str]):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant tasked with summarizing conversations."},
                {"role": "user", "content": f"Please summarize the following conversation:\n\n{' '.join(messages)}"}
            ],
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
