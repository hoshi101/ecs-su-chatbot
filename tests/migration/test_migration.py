#!/usr/bin/env python3
"""
Migration Test Script for FSS Hero Chatbot
Tests all new components after migration to Qdrant + Gemini + BGE-M3

Usage:
    python test_migration.py

This script will test:
- Import of all new dependencies
- Configuration loading
- BGE-M3 embeddings initialization
- Qdrant connection (if credentials available)
- Gemini model initialization (if credentials available)
"""

import os
import sys
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("🧪 FSS Hero Chatbot Migration Test")
print("=" * 50)
print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test 1: Import Dependencies
print("📦 Testing imports...")
try:
    # Core dependencies
    import langchain
    import langchain_core
    import langchain_community
    print("✅ LangChain core imports successful")

    # Qdrant dependencies
    import qdrant_client
    import langchain_qdrant
    print("✅ Qdrant dependencies imported successfully")

    # Google/Gemini dependencies
    import langchain_google_genai
    import google.generativeai
    print("✅ Google/Gemini dependencies imported successfully")

    # Embeddings dependencies
    import langchain_huggingface
    import sentence_transformers
    print("✅ Embeddings dependencies imported successfully")

    # LangGraph
    import langgraph
    print("✅ LangGraph imported successfully")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Run: pip install -r requirements.txt")
    sys.exit(1)

print()

# Test 2: Configuration Loading
print("⚙️  Testing configuration...")
try:
    from dotenv import load_dotenv
    load_dotenv()

    from backend.config import (
        QDRANT_API_KEY, QDRANT_URL, QDRANT_COLLECTION_NAME,
        GOOGLE_API_KEY, TAVILY_API_KEY, EMBED_MODEL, EMBED_DIMENSIONS
    )

    print("✅ Configuration loaded successfully")
    print(f"   📊 Embedding model: {EMBED_MODEL}")
    print(f"   📏 Embedding dimensions: {EMBED_DIMENSIONS}")
    print(f"   🗂️  Collection name: {QDRANT_COLLECTION_NAME}")

    # Check for API keys (without exposing them)
    credentials_status = {
        "Qdrant API Key": "✅ Set" if QDRANT_API_KEY else "❌ Missing",
        "Qdrant URL": "✅ Set" if QDRANT_URL else "❌ Missing",
        "Google API Key": "✅ Set" if GOOGLE_API_KEY else "❌ Missing",
        "Tavily API Key": "✅ Set" if TAVILY_API_KEY else "❌ Missing"
    }

    for name, status in credentials_status.items():
        print(f"   🔑 {name}: {status}")

except Exception as e:
    print(f"❌ Configuration error: {e}")
    print("💡 Check your .env file or copy from .env.example")

print()

# Test 3: BGE-M3 Embeddings
print("🔤 Testing BGE-M3 embeddings...")
try:
    from backend.vectorstore import BGEEmbedder

    print("   📥 Initializing BGE-M3 embeddings...")
    embedder = BGEEmbedder()
    print("✅ BGE-M3 embeddings initialized successfully")

    # Test embedding a simple query
    test_text = "Hello world"
    print(f"   🧪 Testing embedding for: '{test_text}'")
    embedding = embedder.embed_query(test_text)
    print(f"✅ Embedding successful! Dimension: {len(embedding)}")

except Exception as e:
    print(f"❌ BGE-M3 embeddings error: {e}")
    print("💡 This might be the first run - BGE-M3 model (~2GB) will be downloaded")

print()

# Test 4: Qdrant Connection
print("🗄️  Testing Qdrant connection...")
if QDRANT_API_KEY and QDRANT_URL:
    try:
        from qdrant_client import QdrantClient

        print(f"   🔌 Connecting to Qdrant: {QDRANT_URL[:30]}...")
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=10)

        # Test connection
        collections = client.get_collections()
        print(f"✅ Qdrant connection successful!")
        print(f"   📚 Found {len(collections.collections)} collections")

        collection_names = [c.name for c in collections.collections]
        if QDRANT_COLLECTION_NAME in collection_names:
            print(f"   ✅ Target collection '{QDRANT_COLLECTION_NAME}' exists")
        else:
            print(f"   ℹ️  Collection '{QDRANT_COLLECTION_NAME}' not found (will be created)")

    except Exception as e:
        print(f"❌ Qdrant connection error: {e}")
        print("💡 Check your QDRANT_API_KEY and QDRANT_URL")
else:
    print("⚠️  Skipping Qdrant test - credentials not set")

print()

# Test 5: Gemini Model
print("🤖 Testing Gemini model...")
if GOOGLE_API_KEY:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        print("   🔌 Initializing Gemini model...")
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            google_api_key=GOOGLE_API_KEY
        )
        print("✅ Gemini model initialized successfully")

        # Test a simple query (commented out to avoid API costs during testing)
        # print("   🧪 Testing simple query...")
        # response = model.invoke("What is 2+2?")
        # print(f"✅ Gemini response: {response.content}")

    except Exception as e:
        print(f"❌ Gemini model error: {e}")
        print("💡 Check your GOOGLE_API_KEY")
else:
    print("⚠️  Skipping Gemini test - GOOGLE_API_KEY not set")

print()

# Test 6: Backend Components Integration
print("🔧 Testing backend components integration...")
try:
    from backend.vectorstore import get_retriever, add_document_to_vectorstore
    from backend.agent import build_agent

    print("✅ Backend vectorstore functions imported successfully")
    print("✅ Backend agent functions imported successfully")

    if QDRANT_API_KEY and QDRANT_URL:
        try:
            print("   🧪 Testing retriever initialization...")
            retriever = get_retriever()
            print("✅ Retriever initialized successfully")
        except Exception as e:
            print(f"⚠️  Retriever initialization warning: {e}")

    if GOOGLE_API_KEY:
        try:
            print("   🧪 Testing agent build...")
            agent = build_agent()
            print("✅ Agent built successfully")
        except Exception as e:
            print(f"⚠️  Agent build warning: {e}")

except Exception as e:
    print(f"❌ Backend integration error: {e}")

print()

# Summary
print("📋 Migration Test Summary")
print("=" * 30)

missing_requirements = []
if not QDRANT_API_KEY or not QDRANT_URL:
    missing_requirements.append("Qdrant credentials (QDRANT_API_KEY, QDRANT_URL)")
if not GOOGLE_API_KEY:
    missing_requirements.append("Google API key (GOOGLE_API_KEY)")
if not TAVILY_API_KEY:
    missing_requirements.append("Tavily API key (TAVILY_API_KEY)")

if missing_requirements:
    print("⚠️  Missing requirements for full functionality:")
    for req in missing_requirements:
        print(f"   - {req}")
    print()
    print("💡 Set these in your .env file to enable full functionality")
else:
    print("✅ All requirements met!")

print()
print("📚 Next Steps:")
print("1. Set up missing API keys in your .env file")
print("2. Run: python process_documents.py (to process your documents)")
print("3. Start backend: cd backend && uvicorn main:app --reload")
print("4. Start frontend: cd frontend && streamlit run app.py")

print()
print(f"Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🎉 Migration test finished!")