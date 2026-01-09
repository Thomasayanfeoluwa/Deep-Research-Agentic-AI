import gradio as gr
import asyncio
import traceback
from dotenv import load_dotenv
from research_manager import ResearchManager
import logging

# Configure logging to show in terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler('research.log')  
    ]
)

# Load environment variables
load_dotenv(override=True)

# Initialize research manager
research_manager = None

def initialize_manager():
    """Initialize the research manager."""
    global research_manager
    try:
        research_manager = ResearchManager()
        return "✅ Research Manager initialized successfully"
    except Exception as e:
        error_msg = f"❌ Failed to initialize Research Manager: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_msg

async def run_research(query: str):
    """Run research and stream results to Gradio."""
    if not query.strip():
        yield "Please enter a valid research query."
        return
    
    # Initialize manager if not already done
    if research_manager is None:
        init_result = initialize_manager()
        if "❌" in init_result:
            yield init_result
            return
    
    yield "🚀 **Starting research workflow...**\n\n"
    
    try:
        async for chunk in research_manager.run(query):
            yield chunk
            
    except Exception as e:
        error_msg = f"❌ **Error occurred:** {str(e)}"
        print(f"\n{'='*60}")
        print("GRADIO APP ERROR:")
        print(f"{'='*60}")
        print(f"Error: {e}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        yield f"{error_msg}\n\n"
        yield "**Full error traceback:**\n"
        yield f"```\n{traceback.format_exc()}\n```\n\n"
        yield "Please check your API keys and try again."

def run_sync(query: str):
    """Wrapper to run async function synchronously for Gradio."""
    async def run_async():
        results = []
        async for chunk in run_research(query):
            results.append(chunk)
        return "".join(results)
    
    return asyncio.run(run_async())

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="teal",
    neutral_hue="gray"
), title="Deep Research Assistant") as app:
    
    # Header
    gr.Markdown("""
    # 🔬 Deep Research Assistant
    
    *Get comprehensive, AI-powered research reports on any topic.*
    """)
    
    # Status display
    status_display = gr.Markdown("**Status:** Initializing...")
    
    with gr.Row():
        with gr.Column(scale=3):
            # Input section
            query_input = gr.Textbox(
                label="Research Topic",
                placeholder="e.g., What are the latest developments in quantum computing?",
                lines=3,
                max_lines=5
            )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 Start Research", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ Clear", variant="secondary")
            
            # Terminal output simulation
            with gr.Accordion("📟 Terminal Output (Live Logs)", open=False):
                terminal_output = gr.Textbox(
                    label="",
                    value="Terminal output will appear here during research...",
                    lines=10,
                    max_lines=20,
                    interactive=False
                )
        
        with gr.Column(scale=7):
            # Output section
            output = gr.Markdown(
                label="Research Report",
                value="### 📋 Your research report will appear here...\n\nEnter a topic and click 'Start Research'"
            )
    
    # Initialize on load
    app.load(fn=initialize_manager, outputs=status_display)
    
    # Event handlers
    def on_submit(query):
        return "**Status:** Research in progress... 🔄", "Starting research...\n"
    
    def on_clear():
        return "", "### 📋 Enter a new research topic...", "**Status:** Ready", "Cleared"
    
    def update_terminal():
        """Update terminal output (simulated - in real app, you'd stream logs)"""
        return "Research started...\nCheck console for detailed logs."
    
    # Connect events
    submit_event = submit_btn.click(
        fn=on_submit,
        inputs=query_input,
        outputs=[status_display, terminal_output]
    ).then(
        fn=update_terminal,
        outputs=terminal_output
    ).then(
        fn=run_sync,
        inputs=query_input,
        outputs=output
    ).then(
        fn=lambda: "**Status:** Complete ✅",
        outputs=status_display
    ).then(
        fn=lambda: "Research completed! ✅\nCheck the report above.",
        outputs=terminal_output
    )
    
    query_input.submit(
        fn=on_submit,
        inputs=query_input,
        outputs=[status_display, terminal_output]
    ).then(
        fn=update_terminal,
        outputs=terminal_output
    ).then(
        fn=run_sync,
        inputs=query_input,
        outputs=output
    ).then(
        fn=lambda: "**Status:** Complete ✅",
        outputs=status_display
    ).then(
        fn=lambda: "Research completed! ✅",
        outputs=terminal_output
    )
    
    clear_btn.click(
        fn=on_clear,
        inputs=[],
        outputs=[query_input, output, status_display, terminal_output]
    )

# Launch the app
if __name__ == "__main__":
    print("="*60)
    print("🔬 Deep Research Assistant - Starting up...")
    print("="*60)
    
    # Initialize before launching
    init_result = initialize_manager()
    print(init_result)
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True,  # Show detailed errors in Gradio
        debug=True  # Enable debug mode
    )