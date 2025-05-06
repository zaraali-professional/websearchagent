from nicegui import ui
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
import asyncio
import os
load_dotenv()

# Initialize the Agent with detailed instructions
web_search_agent = Agent(
    name="Professional Web Researcher",
    model=Groq(id="llama3-8b-8192", temperature=0.3, max_tokens=1024,api_key=os.getenv("GROQ_API_KEY")),
    tools=[DuckDuckGo()],
    instructions="""
You are a senior web search assistant providing comprehensive, well-structured answers with proper sourcing. Follow these guidelines:

1. Response Structure:
   - Start with a concise 1-2 sentence overview
   - Use sections with ## headers for key categories
   - Present items as numbered bullet points with sub-bullets
   - Include 2-3 relevant links per section from authoritative sources

2. Formatting Rules:
   - **Bold** key terms and section titles
   - Use italic for emphasis in explanations
   - Maintain professional academic tone
   - Always hyperlink sources using [Source Name](URL)
   - Add ➤ arrows before main points
   - Use ### for subsection headers

3. Source Requirements:
   - Prioritize .gov, .edu, and official organization sites
   - Include at least 3 different domains per response
   - Verify link accessibility before inclusion

Example Structure:
**Overview**  
[Concise summary of main findings]

### Key Category 1
➤ **Main Point 1**  
   - Supporting detail [Source 1](link)
   - Additional context [Source 2](link)

### Key Category 2
➤ **Main Point 2**  
   - Comparative analysis [Source 3](link)
   - Statistical data [Source 4](link)

**Conclusion**  
[Final synthesized insights with top recommendations]
""",
    show_tool_calls=False,
    markdown=True,
    debug_mode=False,
)

# Custom CSS for professional appearance
ui.add_head_html('''
<style>
    .pro-response {
        font-family: 'Segoe UI', system-ui, sans-serif;
        line-height: 1.6;
        padding: 1.5rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .pro-response h2 {
        color: #1a365d;
        font-size: 1.4rem;
        margin-top: 1.5rem;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    .pro-response h3 {
        color: #2d3748;
        font-size: 1.2rem;
        margin: 1rem 0 0.5rem;
    }
    .pro-response ul {
        padding-left: 1.5rem;
        margin: 0.75rem 0;
    }
    .pro-response li {
        margin-bottom: 0.5rem;
    }
    .source-link {
        color: #2b6cb0;
        text-decoration: none;
        font-weight: 500;
    }
</style>
''')

# App layout
with ui.card().classes('w-full max-w-3xl mx-auto mt-8 bg-gradient-to-b from-gray-50 to-white'):
    with ui.row().classes('w-full items-center gap-4 mb-6'):
        ui.icon('search', size='2rem', color='#1d4ed8').classes('shrink-0')
        ui.markdown("### Professional Web Research Assistant").classes('text-2xl font-bold text-gray-800')

    with ui.column().classes('w-full gap-4'):
        prompt_input = ui.textarea(
            label="Research Query",
            placeholder="Enter your research question (e.g. Analyze renewable energy initiatives in Scandinavia)",
        ).props('''
            autogrow outlined rounded
            label-color="blue-10"
            input-class="font-medium"
        ''').classes('w-full')

        response_area = ui.column().classes('pro-response gap-4')

        loading = ui.linear_progress().props('instant-feedback indeterminate').classes(
            'absolute top-0 left-0 w-full h-1').style('display: none')

    # Handle search
    async def handle_search():
        query = prompt_input.value.strip()
        if not query:
            ui.notify("Please enter a research question", color='negative')
            return

        response_area.clear()
        loading.style('display: block')
        ui.notify("Analyzing your query...", type='ongoing', timeout=5000)

        try:
            loop = asyncio.get_running_loop()
            with response_area:
                with ui.column().classes('w-full gap-4'):
                    ui.spinner('dots', size='lg', color='blue').classes('self-center')

            result = await loop.run_in_executor(None, lambda: web_search_agent.run(query))

            response_area.clear()
            with response_area:
                ui.markdown(result.content).classes('w-full animate-fade-in')

            ui.notify("Research complete", color='positive', icon='check_circle')

        except Exception as e:
            ui.notify(f"Research error: {str(e)}", color='negative')
            response_area.clear()
            with response_area:
                ui.markdown(f"**System Error**\n```\n{str(e)}\n```").classes('text-red-600 bg-red-50 p-4 rounded')

        finally:
            loading.style('display: none')

    # Button section
    with ui.row().classes('w-full justify-end gap-2'):
        ui.button('Clear', on_click=lambda: [prompt_input.set_value(''), response_area.clear()]).props('flat color=grey-7')
        ui.button('Generate Report', on_click=handle_search).props('icon=search').classes('bg-blue-800 text-white shadow-lg hover:shadow-xl transition-shadow')

# Launch the app
ui.run(
    title="Professional Web Search Assistant",
    reload=False,
    favicon="https://cdn-icons-png.flaticon.com/512/3271/3271408.png",
    dark=False
)
