"""
AI Chat Service for Strategy Refinement using Emergent LLM Key
Phase 4 Implementation - Enhanced with Chat Functionality
"""
import os
import asyncio
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIStrategyService:
    """
    AI Service for trading strategy generation and refinement
    Uses Emergent LLM Key with OpenAI models
    """
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY environment variable not set")
        self.model = "gpt-4o-mini"
        self.provider = "openai"
    
    async def _get_chat_client(self, session_id: str, system_message: str):
        """Get an LLM chat client"""
        from emergentintegrations.llm.chat import LlmChat
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=session_id,
            system_message=system_message
        )
        chat.with_model(self.provider, self.model)
        return chat
    
    async def refine_strategy(self, user_message: str, conversation_history: List[Dict], 
                              category: str = "day_trading") -> str:
        """
        Refine a trading strategy through conversation
        
        Args:
            user_message: User's current message
            conversation_history: Previous messages in the conversation
            category: Trading category (day_trading, swing_trading, long_term)
        
        Returns:
            AI response with strategy refinement suggestions
        """
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        system_message = f"""You are an expert quantitative trading strategist specializing in {category.replace('_', ' ')} strategies.

Your role is to help users develop and refine their trading strategies through conversation.
When discussing strategies:
1. Ask clarifying questions about entry/exit conditions, position sizing, and risk management
2. Suggest improvements based on best practices
3. Help users think through edge cases and market conditions
4. Keep responses concise but informative
5. When the user says they're ready or asks to generate code, provide a clear summary of the final strategy

Format your responses in a helpful, educational manner."""
        
        session_id = f"strategy_refinement_{hash(str(conversation_history)[:100])}"
        
        try:
            chat = await self._get_chat_client(session_id, system_message)
            
            # Build context from history
            context = ""
            if conversation_history:
                context = "Previous conversation:\n"
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    context += f"{role.capitalize()}: {content}\n"
                context += "\n"
            
            full_message = context + f"User: {user_message}"
            user_msg = UserMessage(text=full_message)
            
            response = await chat.send_message(user_msg)
            return response
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    async def generate_strategy_code(self, strategy_description: str, category: str) -> Tuple[str, str]:
        """
        Generate Python trading strategy code from natural language description
        
        Args:
            strategy_description: Natural language strategy description
            category: Trading category
        
        Returns:
            Tuple of (generated_code, error_message)
        """
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        system_message = """You are an expert quantitative trading strategy developer.
Generate clean, executable Python code only. No explanations, no markdown formatting.
The code must define two functions: entry_condition and exit_condition."""
        
        prompt = f"""Convert the following {category.replace('_', ' ')} trading strategy into executable Python code.

Strategy Description: {strategy_description}

Requirements:
1. Define entry_condition(data, index) function returning True/False
   - data: pandas DataFrame with columns: Date, Open, High, Low, Close, Volume
   - index: current row index
2. Define exit_condition(data, index, entry_price, entry_index) function returning True/False
   - entry_price: price at which position was entered
   - entry_index: index when position was entered
3. Handle edge cases (insufficient data, beginning of dataframe)
4. Use simple moving averages or other calculations directly on the data
5. Include any stop-loss or take-profit logic mentioned

Output ONLY the Python code, nothing else. Example structure:

def entry_condition(data, index):
    if index < 20:  # Need enough data
        return False
    # Your entry logic here
    return True or False

def exit_condition(data, index, entry_price, entry_index):
    current_price = data.iloc[index]['Close']
    # Your exit logic here
    return True or False"""
        
        session_id = f"code_gen_{hash(strategy_description)}"
        
        try:
            chat = await self._get_chat_client(session_id, system_message)
            user_msg = UserMessage(text=prompt)
            
            response = await chat.send_message(user_msg)
            
            # Clean up response
            code = response.strip()
            if code.startswith('```python'):
                code = code.replace('```python', '').replace('```', '').strip()
            elif code.startswith('```'):
                code = code.replace('```', '').strip()
            
            # Basic validation
            if 'def entry_condition' not in code or 'def exit_condition' not in code:
                return "", "Generated code missing required functions. Please refine your strategy description."
            
            return code, ""
            
        except Exception as e:
            return "", f"AI code generation failed: {str(e)}"
    
    async def summarize_strategy(self, conversation_history: List[Dict]) -> str:
        """
        Summarize the strategy from conversation history into a clear description
        
        Args:
            conversation_history: Full conversation history
        
        Returns:
            Clean strategy summary
        """
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        system_message = """You are a trading strategy summarizer.
Extract and summarize the final trading strategy from the conversation.
Provide a clear, concise description that includes:
1. Entry conditions
2. Exit conditions
3. Position sizing rules (if mentioned)
4. Stop-loss/take-profit levels (if mentioned)
5. Any other relevant parameters

Format the summary as a clear strategy description that can be converted to code."""
        
        conversation_text = "\n".join([
            f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}"
            for msg in conversation_history
        ])
        
        prompt = f"""Summarize the final trading strategy from this conversation:

{conversation_text}

Provide a clear, technical summary of the strategy."""
        
        session_id = f"strategy_summary_{hash(conversation_text[:100])}"
        
        try:
            chat = await self._get_chat_client(session_id, system_message)
            user_msg = UserMessage(text=prompt)
            
            response = await chat.send_message(user_msg)
            return response
            
        except Exception as e:
            return f"Could not summarize strategy: {str(e)}"


# Synchronous wrapper for Django views
def run_async(coro):
    """Run async coroutine in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


class SyncAIStrategyService:
    """Synchronous wrapper for AIStrategyService"""
    
    def __init__(self):
        self._async_service = AIStrategyService()
    
    def refine_strategy(self, user_message: str, conversation_history: List[Dict], 
                       category: str = "day_trading") -> str:
        return run_async(
            self._async_service.refine_strategy(user_message, conversation_history, category)
        )
    
    def generate_strategy_code(self, strategy_description: str, category: str) -> Tuple[str, str]:
        return run_async(
            self._async_service.generate_strategy_code(strategy_description, category)
        )
    
    def summarize_strategy(self, conversation_history: List[Dict]) -> str:
        return run_async(
            self._async_service.summarize_strategy(conversation_history)
        )
