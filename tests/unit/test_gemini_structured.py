"""Test Gemini structured output to isolate the hanging issue."""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Literal
from src.backend.core.config import GOOGLE_API_KEY
import time

class RouteDecision(BaseModel):
    route: Literal["rag", "web", "answer", "end"]
    reply: str | None = Field(None, description="Filled only when route == 'end'")

print("Testing Gemini with structured output...")
print("-" * 50)

# Test 1: Regular Gemini call (no structured output)
print("\nTest 1: Regular Gemini call...")
try:
    start = time.time()
    regular_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=GOOGLE_API_KEY
    )
    response = regular_llm.invoke([HumanMessage(content="Say 'OK'")])
    elapsed = time.time() - start
    print(f"✅ Regular call successful ({elapsed:.2f}s): {response.content}")
except Exception as e:
    print(f"❌ Regular call failed: {e}")

# Test 2: Gemini with structured output
print("\nTest 2: Gemini with structured output...")
try:
    start = time.time()
    structured_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=GOOGLE_API_KEY
    ).with_structured_output(RouteDecision)

    messages = [
        ("system", "You are a router. Choose route: 'rag', 'web', 'answer', or 'end'."),
        ("user", "What is stop loss?")
    ]

    print("Invoking structured output...")
    result = structured_llm.invoke(messages)
    elapsed = time.time() - start
    print(f"✅ Structured output successful ({elapsed:.2f}s)")
    print(f"Result type: {type(result)}")
    print(f"Route: {result.route}")
    print(f"Reply: {result.reply}")

except Exception as e:
    print(f"❌ Structured output failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test complete!")
