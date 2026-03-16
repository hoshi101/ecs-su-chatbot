# HERO Bot Functional Parity Test Plan

## Overview
This comprehensive test plan validates functional parity between the current LangGraph-based HERO Bot implementation and the reference Agno-based implementation.

## Implementation Comparison

### Current Implementation (LangGraph)
- **Architecture**: FastAPI backend + Streamlit frontend
- **Agents**: LangGraph with Gemini models (gemini-2.5-flash)
- **Web Search**: Tavily API
- **Embeddings**: BGE-M3 with Qdrant vector store
- **Collection**: "hero-bot-bge-m3"
- **Temperature**: 0.3 (financial accuracy)

### Reference Implementation (Agno)
- **Architecture**: Single Streamlit file with Agno agents
- **Agents**: Agno with Gemini models (gemini-1.5-flash)
- **Web Search**: Exa API
- **Embeddings**: BGE-M3 with Qdrant vector store
- **Collection**: "hero-bot-bge-m3"
- **Temperature**: 0.3 (financial accuracy)

## Test Categories

## 1. Core Functionality Tests

### 1.1 Query Enhancement Tests

**Purpose**: Validate that both implementations enhance queries identically

**Test Cases**:

| Test ID | Original Query | Expected Enhancement Pattern | Success Criteria |
|---------|---------------|------------------------------|------------------|
| QE-001 | "How do I use stop loss?" | Should expand to include "stop loss orders", "Finansia Hero trading platform", "order types", "risk management" | Both implementations produce functionally equivalent enhanced queries |
| QE-002 | "Chart not working" | Should expand to include "chart display issues", "technical analysis tools", "charting functionality", "Finansia Hero platform" | Enhanced queries address same core concepts |
| QE-003 | "What are the platform features?" | Should expand to include "complete overview", "Finansia Hero trading platform features", "tools", "functionality" | Both produce comprehensive platform-focused queries |
| QE-004 | "deposit money" | Should expand to include "deposit funds", "account funding", "payment methods" | Both handle financial terminology consistently |
| QE-005 | "MT4 connection" | Should expand to include platform integration, trading platform connectivity | Both handle technical platform terms |

**Validation Method**:
- Compare enhancement patterns rather than exact text
- Focus on key concepts and terminology inclusion
- Both should improve query specificity and searchability

### 1.2 Routing Decision Tests

**Purpose**: Ensure both implementations make equivalent routing decisions

**Test Cases**:

| Test ID | Query | Context | Expected Route | Success Criteria |
|---------|--------|---------|---------------|------------------|
| RT-001 | "How to set up stop loss orders?" | Default settings | RAG | Both route to knowledge base for platform features |
| RT-002 | "What's the latest Bitcoin price?" | Web search enabled | WEB | Both route to web search for current market data |
| RT-003 | "Hello there!" | Default settings | END/ANSWER | Both handle greetings appropriately |
| RT-004 | "How to reset password?" | Default settings | RAG | Both route to knowledge base for account management |
| RT-005 | "Current EUR/USD rate?" | Web search disabled | RAG | Both fallback to RAG when web disabled |
| RT-006 | "Platform trading fees?" | Force web search ON | WEB | Both respect force web search setting |

**Validation Method**:
- Compare final routing decisions
- Verify override logic works consistently
- Check web search enable/disable behavior

### 1.3 Knowledge Base Retrieval Tests

**Purpose**: Validate RAG search behavior and similarity thresholds

**Test Cases**:

| Test ID | Query | Similarity Threshold | Expected Behavior | Success Criteria |
|---------|--------|---------------------|-------------------|------------------|
| KB-001 | "stop loss configuration" | 0.7 | Should retrieve relevant docs if available | Both return same relevance level |
| KB-002 | "completely random query xyz" | 0.7 | Should return empty/no results | Both handle irrelevant queries similarly |
| KB-003 | "trading platform features" | 0.5 | Should retrieve broader results | Both adjust to lower threshold |
| KB-004 | "chart analysis tools" | 0.9 | Should be very selective | Both handle high threshold similarly |
| KB-005 | "account management" | 0.7 | Should find account-related docs | Both retrieve relevant account info |

**Validation Method**:
- Compare number of documents retrieved
- Assess relevance quality subjectively
- Check threshold behavior consistency

### 1.4 Web Search Integration Tests

**Purpose**: Validate web search behavior (noting different APIs)

**Test Cases**:

| Test ID | Query | Web Setting | Expected Behavior | Success Criteria |
|---------|--------|-------------|-------------------|------------------|
| WS-001 | "latest market news" | Enabled | Should search external sources | Both attempt web search |
| WS-002 | "Bitcoin price today" | Enabled | Should find current market data | Both return market information |
| WS-003 | "trading strategies" | Disabled | Should not use web search | Both respect disabled setting |
| WS-004 | "Finansia Hero updates" | Force Web ON | Should force web search | Both override to web search |
| WS-005 | "platform troubleshooting" | Auto-decide | Should try RAG first | Both follow same decision logic |

**Validation Method**:
- Focus on search initiation behavior rather than exact results
- Compare search domain restrictions
- Verify configuration respect

## 2. Configuration Tests

### 2.1 Similarity Threshold Configuration

**Test Cases**:

| Test ID | Threshold | Query Type | Expected Behavior | Success Criteria |
|---------|-----------|------------|-------------------|------------------|
| ST-001 | 0.3 (Low) | "general trading" | More permissive document retrieval | Both return more results |
| ST-002 | 0.7 (Medium) | "specific platform feature" | Balanced relevance | Both show similar selectivity |
| ST-003 | 0.9 (High) | "exact feature name" | Very strict matching | Both show high selectivity |
| ST-004 | 1.0 (Maximum) | "any query" | Regular search without threshold | Both fallback to regular search |

### 2.2 Web Search Toggle Tests

**Test Cases**:

| Test ID | Setting | Query | Expected Behavior | Success Criteria |
|---------|---------|-------|-------------------|------------------|
| WT-001 | Web Enabled | "market data" | Can use web search | Both allow web search |
| WT-002 | Web Disabled | "market data" | Must use RAG only | Both respect disabled setting |
| WT-003 | Force Web ON | "platform feature" | Override to web | Both force web search |
| WT-004 | Force Web OFF | "market data" | Normal routing | Both follow standard logic |

## 3. Response Quality Tests

### 3.1 Platform-Specific Queries

**Test Cases**:

| Test ID | Query | Expected Response Elements | Success Criteria |
|---------|--------|---------------------------|------------------|
| PQ-001 | "How to place a market order?" | Step-by-step instructions, platform-specific terms | Both provide actionable guidance |
| PQ-002 | "Chart indicators not showing" | Troubleshooting steps, technical solutions | Both offer practical solutions |
| PQ-003 | "Account verification process" | Account management procedures | Both explain verification clearly |
| PQ-004 | "Risk management settings" | Risk controls, safety features | Both emphasize risk management |

### 3.2 External Knowledge Queries

**Test Cases**:

| Test ID | Query | Expected Response Elements | Success Criteria |
|---------|--------|---------------------------|------------------|
| EQ-001 | "Current forex market trends" | External source attribution, market insights | Both provide market information |
| EQ-002 | "Trading education resources" | External resources, learning materials | Both suggest helpful resources |
| EQ-003 | "Economic calendar events" | Current events, market impact | Both provide relevant information |

## 4. Edge Cases and Error Handling

### 4.1 System Limitation Tests

**Test Cases**:

| Test ID | Scenario | Expected Behavior | Success Criteria |
|---------|----------|-------------------|------------------|
| EH-001 | Empty knowledge base | Graceful fallback message | Both handle missing KB gracefully |
| EH-002 | Web search API failure | Error handling, fallback behavior | Both handle API errors similarly |
| EH-003 | Very long query (500+ chars) | Query processing, response generation | Both handle long queries |
| EH-004 | Non-English query | Language handling or appropriate error | Both handle language consistently |
| EH-005 | Malformed/special characters | Input sanitization | Both handle special input safely |

### 4.2 Configuration Edge Cases

**Test Cases**:

| Test ID | Scenario | Expected Behavior | Success Criteria |
|---------|----------|-------------------|------------------|
| EC-001 | Threshold = 0.0 | Should retrieve all documents | Both handle minimum threshold |
| EC-002 | Invalid API keys | Appropriate error messages | Both show helpful error info |
| EC-003 | Network connectivity issues | Timeout handling, error messages | Both handle network problems |

## 5. User Experience Consistency Tests

### 5.1 Interface Behavior

**Test Cases**:

| Test ID | Action | Expected UI Behavior | Success Criteria |
|---------|--------|---------------------|------------------|
| UI-001 | Toggle web search ON | Interface shows setting active | Both UIs reflect state change |
| UI-002 | Adjust similarity threshold | Immediate setting update | Both update settings consistently |
| UI-003 | Clear conversation | Chat history cleared | Both clear history completely |
| UI-004 | Query enhancement display | Shows original vs enhanced query | Both display enhancement info |
| UI-005 | Source document display | Shows relevant source information | Both provide source details |

### 5.2 Response Timing

**Test Cases**:

| Test ID | Query Type | Expected Response Time | Success Criteria |
|---------|------------|----------------------|------------------|
| PT-001 | Simple RAG query | < 5 seconds | Both respond within reasonable time |
| PT-002 | Web search query | < 10 seconds | Both handle web search timing |
| PT-003 | Complex multi-step query | < 15 seconds | Both process complex queries efficiently |

## Test Execution Framework

### Sample Test Queries by Category

#### Platform-Specific Questions
```
1. "How do I set up stop loss orders in Finansia Hero?"
2. "My charts are not loading properly, what should I do?"
3. "How can I change my account leverage settings?"
4. "What trading instruments are available on the platform?"
5. "How to use the technical analysis tools?"
6. "Account verification is pending, what's next?"
7. "How to deposit funds into my trading account?"
8. "Platform keeps logging me out, how to fix?"
9. "How to set up price alerts?"
10. "What are the trading fees and commissions?"
```

#### General Trading Questions
```
1. "What's the current Bitcoin price?"
2. "How does forex trading work?"
3. "What are the best trading strategies for beginners?"
4. "Current market volatility trends?"
5. "Economic calendar for this week?"
6. "Risk management best practices?"
7. "How to read candlestick charts?"
8. "What moves currency prices?"
9. "Trading psychology tips?"
10. "Market analysis techniques?"
```

#### Edge Case Queries
```
1. "Hello" (greeting)
2. "asldkfj asldfkj" (nonsense)
3. "" (empty query)
4. "How to hack the platform?" (inappropriate)
5. "What's the weather today?" (off-topic)
6. "Je voudrais trader" (non-English)
7. "URGENT!!!! HELP!!!" (emotional/caps)
8. "Tell me a joke" (entertainment)
9. "What's 2+2?" (basic math)
10. "Who is the CEO?" (company info)
```

## Success Criteria

### Primary Success Metrics
1. **Query Enhancement Consistency**: 90%+ of queries produce functionally equivalent enhanced versions
2. **Routing Decision Parity**: 95%+ of routing decisions match between implementations
3. **Response Quality Equivalence**: Subjective assessment showing both provide helpful, accurate information
4. **Configuration Behavior**: 100% consistency in respecting user settings (web search, thresholds)
5. **Error Handling**: Both implementations handle errors gracefully with appropriate messages

### Secondary Success Metrics
1. **Response Time Similarity**: Response times within 50% of each other for equivalent operations
2. **Source Attribution**: Both implementations provide appropriate source information
3. **User Experience**: Interface behaviors are consistent and intuitive

## Validation Methodology

### Automated Testing
1. **Query Enhancement Comparison**: Automated script to compare enhancement patterns
2. **Routing Decision Validation**: Automated testing of routing logic with various configurations
3. **Configuration Testing**: Automated verification of settings behavior

### Manual Testing
1. **Response Quality Assessment**: Human evaluation of response helpfulness and accuracy
2. **User Experience Testing**: Manual testing of UI/UX consistency
3. **Edge Case Validation**: Manual testing of unusual scenarios

### Comparison Framework

#### Test Execution Process
1. **Setup Phase**: Configure both implementations with identical settings
2. **Test Phase**: Execute same queries with same configurations
3. **Comparison Phase**: Compare results using defined criteria
4. **Documentation Phase**: Record findings and discrepancies

#### Evaluation Criteria
- **Functional Equivalence**: Core functionality produces equivalent results
- **Behavioral Consistency**: Similar responses to configuration changes
- **Error Handling Parity**: Consistent error handling and recovery
- **Performance Similarity**: Comparable response times and resource usage

### Test Reporting

#### Test Results Format
```
Test ID: QE-001
Query: "How do I use stop loss?"
Current Implementation Enhancement: "[Enhanced query result]"
Reference Implementation Enhancement: "[Enhanced query result]"
Functional Parity: PASS/FAIL
Notes: [Any observations or discrepancies]
```

#### Summary Report Structure
1. **Executive Summary**: Overall parity assessment
2. **Detailed Results**: Test-by-test breakdown
3. **Critical Issues**: Any blocking functional differences
4. **Recommendations**: Suggested fixes or improvements
5. **Validation Certificate**: Final parity confirmation

## Implementation Notes

### Key Areas of Focus
1. **Query Enhancement Logic**: Ensure identical enhancement patterns
2. **Routing Decisions**: Verify same decision-making logic
3. **Threshold Behavior**: Consistent similarity threshold handling
4. **Web Search Integration**: Functional equivalence despite different APIs (Tavily vs Exa)
5. **Error Recovery**: Similar graceful degradation patterns

### Acceptable Differences
1. **API Response Variations**: Different web search APIs may return different but equivalent results
2. **Performance Differences**: Slight variations in response time due to architectural differences
3. **UI Styling**: Visual differences are acceptable if functionality is equivalent
4. **Debug Information**: Different trace/debug info is acceptable if core functionality matches

### Critical Requirements
1. **Same Knowledge Base**: Both must use "hero-bot-bge-m3" collection
2. **Same Model Settings**: Identical Gemini model configuration with temperature 0.3
3. **Same Domain Restrictions**: Identical search domain limitations
4. **Same Enhancement Logic**: Query enhancement must follow same patterns
5. **Same Routing Logic**: Decision-making process must be equivalent

This comprehensive test plan ensures that both HERO Bot implementations deliver equivalent functionality and user experience while accounting for the underlying architectural differences.