import gradio as gr
import asyncio
from dotenv import load_dotenv
from research_manager import ResearchManager

# Load environment variables
load_dotenv(override=True)

# Initialize research manager
research_manager = ResearchManager()

async def run_research(query: str):
    """Run research and stream results to Gradio."""
    if not query.strip():
        yield "Please enter a valid research query."
        return
    
    yield "🚀 **Starting research workflow...**\n\n"
    
    try:
        current_report = ""
        async for chunk in research_manager.run(query):
            if "Final Research Report" in chunk or "##" in chunk or "- " in chunk:
                current_report += chunk
            yield current_report
            
    except Exception as e:
        yield f"❌ **Error occurred:** {str(e)}\n\nPlease try again."

def run_sync(query: str):
    """Wrapper to run async function synchronously."""
    async def run_async():
        full_output = ""
        async for chunk in run_research(query):
            full_output = chunk
        return full_output
    
    return asyncio.run(run_async())

# Create interface
with gr.Blocks(title="Deep Research Assistant") as app:
    gr.Markdown("# 🔬 Deep Research Assistant")
    
    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                label="Research Topic",
                placeholder="Enter your research query...",
                lines=3
            )
            
            with gr.Row():
                submit_btn = gr.Button("Start Research", variant="primary")
                clear_btn = gr.Button("Clear")
        
        with gr.Column(scale=7):
            output = gr.Markdown(
                label="Research Report",
                value="### Your research report will appear here..."
            )
    
    # Event handlers
    submit_btn.click(
        fn=run_sync,
        inputs=query_input,
        outputs=output,
        show_progress="full"
    )
    
    clear_btn.click(
        fn=lambda: ("", "### Enter a new research query..."),
        inputs=[],
        outputs=[query_input, output]
    )
    
    query_input.submit(
        fn=run_sync,
        inputs=query_input,
        outputs=output,
        show_progress="full"
    )

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False, inbrowser=True)