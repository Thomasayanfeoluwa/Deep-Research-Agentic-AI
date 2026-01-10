import streamlit as st
import asyncio
from dotenv import load_dotenv
from research_manager import ResearchManager

# Load environment variables
load_dotenv(override=True)

# Page config
st.set_page_config(
    page_title="Deep Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 16px;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_manager' not in st.session_state:
    st.session_state.research_manager = ResearchManager()
if 'report' not in st.session_state:
    st.session_state.report = ""
if 'running' not in st.session_state:
    st.session_state.running = False

# Header
st.title("🔬 Deep Research Assistant")
st.markdown("*Powered by AI-driven multi-agent research workflow*")
st.divider()

# Input section
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "Research Topic",
        placeholder="Enter your research query...",
        disabled=st.session_state.running
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    start_btn = st.button(
        "🚀 Start Research",
        type="primary",
        disabled=st.session_state.running or not query.strip(),
        use_container_width=True
    )

st.divider()

# Main content area
if start_btn and query.strip():
    st.session_state.running = True
    st.session_state.report = ""
    
    # Status container
    status_container = st.container()
    
    # Report container
    report_container = st.container()
    
    with status_container:
        st.subheader("📊 Research Progress")
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
    
    async def run_research():
        """Run research and update UI."""
        status_updates = []
        node_count = 0
        total_nodes = 4  # planner, researcher, writer, notifier
        
        try:
            async for chunk in st.session_state.research_manager.run(query):
                # Track status updates
                if "**" in chunk and "COMPLETE" in chunk:
                    status_updates.append(chunk.strip())
                    node_count += 1
                    progress = min(node_count / total_nodes, 1.0)
                    progress_bar.progress(progress)
                    
                    # Display status
                    status_text = "\n\n".join(status_updates)
                    status_placeholder.markdown(status_text)
                
                # Accumulate report
                elif "##" in chunk or "- " in chunk or len(chunk) > 50:
                    st.session_state.report += chunk
                    
                    # Update report display
                    with report_container:
                        st.markdown(st.session_state.report)
            
            # Mark as complete
            progress_bar.progress(1.0)
            status_placeholder.success("✅ Research completed successfully!")
            
        except Exception as e:
            status_placeholder.error(f"❌ Error: {str(e)}")
            with report_container:
                st.error("Research failed. Please check your API keys and try again.")
        
        finally:
            st.session_state.running = False
    
    # Run async function
    asyncio.run(run_research())

elif st.session_state.report:
    # Display previous report
    st.markdown(st.session_state.report)

else:
    # Welcome message
    st.info("👆 Enter a research topic above to get started")
    
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        This AI research assistant uses a multi-agent workflow:
        
        1. **📋 Planning** - Breaks down your query into focused search topics
        2. **🔍 Research** - Executes web searches in parallel
        3. **📝 Writing** - Synthesizes findings into a comprehensive report
        4. **🔔 Notification** - Sends completion alert to your device
        
        The system uses advanced LLMs and real-time web data to deliver accurate, 
        detailed research reports on any topic.
        """)
    
    with st.expander("💡 Example queries"):
        st.markdown("""
        - "Latest developments in quantum computing"
        - "Comparison of React vs Vue.js in 2026"
        - "Impact of AI on healthcare diagnostics"
        - "Current trends in sustainable energy"
        """)

# Footer
st.divider()
st.caption("Built with LangGraph, Groq, and Streamlit")
