# AI Assistant Chatbot for Finansia Hero Website / Application

**Author:** Mr. Ashirathee Inya\
**University Supervisors:** Assoc. Prof. Dr. Chukiet Sodsri\
**Co-op Organization:** Finansia Syrus Securities Public Company
Limited\
**Co-op Supervisors:** Mr. Kwanchai Klommek

------------------------------------------------------------------------

## ABSTRACT

Finansia Hero's documentation consists of complex PDF manuals with UI
screenshots, comparison tables, and mixed Thai-English content across PC
and Mobile versions, making it difficult for users to locate specific
information efficiently.

This project develops a RAG-based AI chatbot integrated with Gemini to
provide accurate, automated bilingual responses 24/7, processing 1,700+
document chunks from official documentation while reducing support
workload.

------------------------------------------------------------------------

## INTRODUCTION

Finansia HERO is a securities trading platform by Finansia Syrus
Securities PCL, offering desktop (HTS) and mobile applications. Its
documentation consists of PDF manuals with visual-heavy layouts,
screenshots, tables, and Thai-English content, making information
retrieval time-consuming.

Users typically rely on FAQ pages and customer support to find
information. This project introduces an AI system using
Retrieval-Augmented Generation (RAG) that consolidates official
documentation and provides accurate responses 24/7, reducing support
workload and minimizing AI hallucination.

------------------------------------------------------------------------

## OBJECTIVES

-   Develop a RAG-based AI chatbot for answering Finansia Hero platform
    inquiries
-   Transform complex bilingual PDF documentation into a searchable
    vector database
-   Implement intelligent query routing with context-aware response
    generation
-   Provide automated 24/7 bilingual support to reduce workload and
    operational cost

------------------------------------------------------------------------

## METHODOLOGY

The system uses Retrieval-Augmented Generation (RAG) integrated with
Gemini AI.

User queries are matched against official documentation via vector
similarity search. Relevant documents are passed as context to the LLM
for grounded response generation --- reducing hallucination and ensuring
factual accuracy.

------------------------------------------------------------------------

## RESULTS

### System Performance and Capabilities:

-   Processed documents into 1,737+ searchable chunks using semantic and
    similarity search
-   Supports bilingual queries (Thai/English) with automatic language
    detection and query enhancement
-   Intelligent routing classifies queries into 4 paths:
    -   RAG
    -   Web search
    -   Direct answer
    -   Out-of-scope
-   Achieves \~17--33 second response time for full RAG pipeline
    (including LLM-based routing, retrieval, and generation)

------------------------------------------------------------------------

## CONCLUSION

This project developed a RAG-based AI chatbot for Finansia HERO that
grounds responses in verified documentation, reducing misinformation
compared to standalone LLM usage.

Intelligent routing and modular design enhance information access while
maintaining reliability. The system enables 24/7 support and serves as a
scalable prototype adaptable to other platforms through knowledge base
replacement.

------------------------------------------------------------------------

## REFERENCES

1.  P. Lewis, et al., "Retrieval-Augmented Generation for
    Knowledge-Intensive NLP Tasks," Advances in Neural Information
    Processing Systems (NeurIPS), 2020.
2.  J. Chen, S. Xiao, P. Zhang, K. Luo, D. Lian, and Z. Liu, "BGE-M3
    Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity
    Text Embeddings Through Self-Knowledge Distillation," arXiv preprint
    arXiv:2402.03216, 2024.
3.  Google DeepMind, "Gemini API Documentation," 2024. Available:
    https://ai.google.dev/
4.  LangChain (2025). LangGraph: Build Stateful Agents. Retrieved from
    https://langchain-ai.github.io/langgraph/
5.  Streamlit Inc., "Streamlit Documentation: Build Data Apps," 2024.
    Available: https://docs.streamlit.io/
6.  Finansia Syrus Securities PCL (2025). Finansia Hero Trading
    Platform. Available: https://www.finansiahero.com/
