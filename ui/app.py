"""Streamlit UI for RAG System."""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any, List

# Page config
st.set_page_config(
    page_title="RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .citation {
        background-color: #e8f4f8;
        padding: 0.5rem;
        border-left: 3px solid #667eea;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)


def api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Make API request."""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def display_citations(citations: Dict[str, Any]):
    """Display citations."""
    if not citations:
        return
    
    st.markdown("### 📚 Sources")
    for citation_num, citation_data in citations.items():
        with st.expander(f"Source [{citation_num}]"):
            st.markdown(f"**Source:** {citation_data['source']}")
            st.markdown(f"**Relevance Score:** {citation_data['score']:.3f}")
            st.markdown(f"**Preview:** {citation_data['content_preview']}")


def main():
    """Main application."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 RAG System</h1>', unsafe_allow_html=True)
    st.markdown("**Production-Grade Retrieval Augmented Generation**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Mode selection
        mode = st.radio(
            "Select Mode",
            ["💬 Query", "📄 Document Ingestion", "📊 Statistics", "🧪 Evaluation"]
        )
        
        st.markdown("---")
        
        # Settings
        st.subheader("Query Settings")
        top_k = st.slider("Number of documents", 1, 10, 5)
        temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
        use_reranking = st.checkbox("Use Reranking", value=True)
        return_context = st.checkbox("Show Context", value=False)
        
        st.markdown("---")
        
        # Health check
        st.subheader("System Status")
        if st.button("Check Health"):
            health = api_request("/health")
            if health:
                st.success(f"Status: {health['status']}")
                st.info(f"Version: {health['version']}")
    
    # Main content based on mode
    if mode == "💬 Query":
        query_mode(top_k, temperature, use_reranking, return_context)
    
    elif mode == "📄 Document Ingestion":
        ingestion_mode()
    
    elif mode == "📊 Statistics":
        statistics_mode()
    
    elif mode == "🧪 Evaluation":
        evaluation_mode()


def query_mode(top_k: int, temperature: float, use_reranking: bool, return_context: bool):
    """Query mode UI."""
    st.header("💬 Ask Questions")
    st.markdown("Ask questions and get answers based on your ingested documents.")
    
    # Chat or Single Query
    query_type = st.radio("Query Type", ["Single Query", "Chat"], horizontal=True)
    
    if query_type == "Single Query":
        single_query_ui(top_k, temperature, use_reranking, return_context)
    else:
        chat_ui(top_k, temperature, use_reranking)


def single_query_ui(top_k: int, temperature: float, use_reranking: bool, return_context: bool):
    """Single query UI."""
    
    # Question input
    question = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="What would you like to know?"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        submit = st.button("🔍 Search", type="primary")
    
    with col2:
        clear = st.button("🗑️ Clear")
    
    if clear:
        st.rerun()
    
    if submit and question:
        with st.spinner("Searching and generating answer..."):
            # Make API request
            result = api_request("/query", "POST", {
                "question": question,
                "top_k": top_k,
                "temperature": temperature,
                "use_reranking": use_reranking,
                "return_context": return_context
            })
            
            if result:
                # Display answer
                st.markdown("### ✨ Answer")
                st.markdown(result["answer"])
                
                # Display metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Citations", result["num_citations"])
                with col2:
                    st.metric("Sources", result["num_sources"])
                
                # Display citations
                if result.get("citations"):
                    display_citations(result["citations"])
                
                # Display context if requested
                if return_context and result.get("context"):
                    st.markdown("### 📄 Retrieved Context")
                    for i, ctx in enumerate(result["context"], 1):
                        with st.expander(f"Document {i} - Score: {ctx['score']:.3f}"):
                            st.markdown(f"**Source:** {ctx['source']}")
                            st.text(ctx["content"])


def chat_ui(top_k: int, temperature: float, use_reranking: bool):
    """Chat UI with conversation history."""
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant"):
                st.markdown(content)
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = api_request("/chat", "POST", {
                    "message": prompt,
                    "chat_history": st.session_state.chat_history,
                    "top_k": top_k,
                    "temperature": temperature,
                    "use_reranking": use_reranking
                })
                
                if result:
                    st.markdown(result["answer"])
                    st.session_state.chat_history = result["chat_history"]
                    
                    # Show citations
                    if result.get("citations"):
                        with st.expander("📚 View Sources"):
                            for citation_num, citation_data in result["citations"].items():
                                st.markdown(f"**[{citation_num}]** {citation_data['source']}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


def ingestion_mode():
    """Document ingestion UI."""
    st.header("📄 Document Ingestion")
    st.markdown("Ingest documents into the RAG system.")
    
    # Ingestion type
    ingest_type = st.radio("Ingestion Type", ["File/URL", "Website Crawl"], horizontal=True)
    
    if ingest_type == "File/URL":
        source = st.text_input(
            "Enter file path or URL:",
            placeholder="e.g., ./documents/paper.pdf or https://example.com/page.html"
        )
    else:
        source = st.text_input(
            "Enter website URL:",
            placeholder="e.g., https://example.com"
        )
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            chunk_strategy = st.selectbox(
                "Chunking Strategy",
                ["recursive", "semantic", "fixed"]
            )
            chunk_size = st.number_input("Chunk Size", 100, 4000, 1000)
        
        with col2:
            chunk_overlap = st.number_input("Chunk Overlap", 0, 1000, 200)
            
            if ingest_type == "Website Crawl":
                max_depth = st.number_input("Max Crawl Depth", 1, 5, 2)
            else:
                max_depth = 1
    
    # Ingest button
    if st.button("📥 Ingest", type="primary"):
        if source:
            with st.spinner("Ingesting documents..."):
                result = api_request("/ingest", "POST", {
                    "source": source,
                    "chunk_strategy": chunk_strategy,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "crawl": ingest_type == "Website Crawl",
                    "max_depth": max_depth
                })
                
                if result:
                    st.success("Ingestion completed!")
                    
                    # Display results
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Documents", result["num_documents"])
                    with col2:
                        st.metric("Chunks", result["num_chunks"])
                    with col3:
                        st.metric("Stored", result["num_stored"])
        else:
            st.warning("Please enter a source.")


def statistics_mode():
    """Statistics and metrics UI."""
    st.header("📊 System Statistics")
    
    # Refresh button
    if st.button("🔄 Refresh"):
        st.rerun()
    
    # Get stats
    stats = api_request("/stats")
    
    if stats:
        # Pipeline Stats
        st.subheader("🔧 Pipeline Configuration")
        pipeline_stats = stats.get("pipeline_stats", {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Vector Store**")
            vector_stats = pipeline_stats.get("vector_store", {})
            st.json(vector_stats)
        
        with col2:
            st.markdown("**Retriever Config**")
            retriever_config = pipeline_stats.get("retriever_config", {})
            st.json(retriever_config)
        
        # System Metrics
        st.subheader("📈 System Metrics")
        metrics = stats.get("metrics", {})
        
        # Query metrics
        st.markdown("**Query Metrics**")
        query_metrics = metrics.get("queries", {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", query_metrics.get("total", 0))
        with col2:
            st.metric("Successful", query_metrics.get("successful", 0))
        with col3:
            st.metric("Failed", query_metrics.get("failed", 0))
        with col4:
            st.metric("Avg Latency", f"{query_metrics.get('avg_latency', 0):.3f}s")
        
        # Ingestion metrics
        st.markdown("**Ingestion Metrics**")
        ingest_metrics = metrics.get("ingestions", {})
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Ingestions", ingest_metrics.get("total", 0))
        with col2:
            st.metric("Total Documents", ingest_metrics.get("total_documents", 0))
        with col3:
            st.metric("Total Chunks", ingest_metrics.get("total_chunks", 0))
        
        # Uptime
        st.markdown("**System Uptime**")
        uptime = metrics.get("uptime_seconds", 0)
        st.info(f"⏱️ Uptime: {uptime:.0f} seconds ({uptime/3600:.2f} hours)")


def evaluation_mode():
    """Evaluation mode UI."""
    st.header("🧪 Evaluation")
    st.markdown("Evaluate RAG system responses.")
    
    st.info("💡 This mode allows you to evaluate the quality of generated answers.")
    
    # Input fields
    question = st.text_area("Question:", height=100)
    answer = st.text_area("Generated Answer:", height=150)
    
    contexts = st.text_area(
        "Retrieved Contexts (one per line):",
        height=150
    )
    
    ground_truth = st.text_area(
        "Ground Truth Answer (optional):",
        height=100
    )
    
    if st.button("📊 Evaluate", type="primary"):
        if question and answer and contexts:
            context_list = [ctx.strip() for ctx in contexts.split("\n") if ctx.strip()]
            
            with st.spinner("Evaluating..."):
                result = api_request("/evaluate", "POST", {
                    "question": question,
                    "answer": answer,
                    "contexts": context_list,
                    "ground_truth": ground_truth if ground_truth else None
                })
                
                if result:
                    st.success("Evaluation complete!")
                    
                    # Display metrics
                    st.subheader("📊 Evaluation Metrics")
                    
                    # Custom metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Answer Length", result.get("answer_length", 0))
                    with col2:
                        st.metric("Citation Count", result.get("citation_count", 0))
                    with col3:
                        st.metric("Context Utilization", f"{result.get('context_utilization', 0):.2%}")
                    
                    # Additional metrics
                    st.json(result)
        else:
            st.warning("Please fill in all required fields.")


if __name__ == "__main__":
    main()

