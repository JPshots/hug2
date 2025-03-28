import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Union

import gradio as gr
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Amazon Review Framework API",
    description="API for Amazon Review Framework - A comprehensive system for creating exceptional product reviews",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IMPORTANT: Explicitly set the framework directory to NEW-SYSTEM
FRAMEWORK_DIR = "NEW-SYSTEM"
logger.info(f"Using directory {FRAMEWORK_DIR} for framework files")

# Check if directory exists
if not os.path.exists(FRAMEWORK_DIR):
    logger.warning(f"Directory {FRAMEWORK_DIR} does not exist!")
    # List all directories at root level
    root_dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    logger.info(f"Available directories at root: {root_dirs}")
else:
    logger.info(f"Directory {FRAMEWORK_DIR} exists")
    # List contents
    files = os.listdir(FRAMEWORK_DIR)
    logger.info(f"Files in {FRAMEWORK_DIR}: {files}")
    # Count JSON files
    json_files = [f for f in files if f.endswith('.json')]
    logger.info(f"Found {len(json_files)} JSON files in {FRAMEWORK_DIR}")

# Check if Anthropic API key is available
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
has_anthropic = ANTHROPIC_API_KEY is not None

if has_anthropic:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info("Anthropic client initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Anthropic client: {str(e)}")
        has_anthropic = False
        client = None
else:
    logger.warning("ANTHROPIC_API_KEY not set. Review generation will be disabled.")
    client = None

# Define Pydantic models for API
class ReviewRequest(BaseModel):
    product_name: str
    product_category: str
    user_experience: str
    include_components: List[str] = []

class ReviewResponse(BaseModel):
    review: str
    components_used: List[str]

# Load all framework files from the directory
def load_framework_files():
    framework_files = {}
    
    if not os.path.exists(FRAMEWORK_DIR):
        logger.warning(f"Framework directory {FRAMEWORK_DIR} does not exist")
        return framework_files
    
    for filename in os.listdir(FRAMEWORK_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(FRAMEWORK_DIR, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    framework_files[filename] = json.load(f)
                    logger.info(f"Loaded framework file: {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
    
    return framework_files

# Function to generate review using Anthropic Claude
async def generate_review(request: ReviewRequest) -> str:
    if not has_anthropic:
        return "Anthropic API key not set. Please configure the ANTHROPIC_API_KEY environment variable to use review generation."
    
    # Load requested framework components
    framework_files = load_framework_files()
    components = {}
    
    if not request.include_components:
        # If no specific components requested, include core components
        default_components = [
            "framework-config.json",
            "review-strategy.json",
            "content-structure.json"
        ]
        for component in default_components:
            if component in framework_files:
                components[component] = framework_files[component]
                logger.info(f"Including default component: {component}")
    else:
        # Include requested components
        for component in request.include_components:
            if not component.endswith(".json"):
                component += ".json"
            if component in framework_files:
                components[component] = framework_files[component]
                logger.info(f"Including requested component: {component}")
    
    # Create prompt for Claude
    prompt = f"""
    You are a professional product reviewer using the Amazon Review Framework.
    
    Product: {request.product_name}
    Category: {request.product_category}
    
    User's experience with the product:
    {request.user_experience}
    
    Using the Amazon Review Framework components below, generate a comprehensive, 
    well-structured review for this product. Follow the framework guidelines for structure,
    content balance, and authenticity.
    
    Framework components to use:
    {json.dumps(components, indent=2)}
    
    Generate a complete review following these framework guidelines.
    """
    
    try:
        message = await client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0.7,
            system="You are a professional product reviewer using the Amazon Review Framework. Generate authentic, helpful reviews based on user experiences.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        logger.error(f"Error generating review with Claude: {str(e)}")
        return f"Error generating review: {str(e)}"

# Function to sync run an async function
def sync_generate_review(product_name, product_category, user_experience, components):
    request = ReviewRequest(
        product_name=product_name,
        product_category=product_category,
        user_experience=user_experience,
        include_components=components
    )
    
    # We need to run the async function in a synchronous context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        review = loop.run_until_complete(generate_review(request))
    finally:
        loop.close()
    
    return review

# Mount static files
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logger.warning(f"Static directory {static_dir} not found")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML page"""
    try:
        if os.path.exists(os.path.join(static_dir, "index.html")):
            with open(os.path.join(static_dir, "index.html"), "r") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
    
    # Fallback HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Amazon Review Framework</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .button {{ display: inline-block; padding: 10px 20px; background-color: #3498db; 
                 color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
        .info {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Amazon Review Framework</h1>
        <p>A comprehensive system for creating exceptional product reviews.</p>
        
        <div class="info">
            <h2>System Status:</h2>
            <p>Framework Directory: {FRAMEWORK_DIR}</p>
            <p>Directory exists: {os.path.exists(FRAMEWORK_DIR)}</p>
            <p>Files in directory: {os.listdir(FRAMEWORK_DIR) if os.path.exists(FRAMEWORK_DIR) else 'Directory not found'}</p>
            <p>JSON files found: {len([f for f in os.listdir(FRAMEWORK_DIR) if f.endswith('.json')]) if os.path.exists(FRAMEWORK_DIR) else 0}</p>
            <p>Anthropic API available: {has_anthropic}</p>
        </div>
        
        <a href="https://jpshots-amazon-review-system.hf.space/gradio/" class="button">Launch Gradio Interface</a>
        
        <h2>API Endpoints:</h2>
        <ul>
            <li>/files - List all available framework files</li>
            <li>/files/{'{filename}'} - Get a specific framework file</li>
            <li>/framework - Get complete framework data</li>
            <li>/generate-review - Generate a review using Claude and the framework</li>
        </ul>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)

@app.get("/files")
async def list_files():
    """
    List all available framework files
    """
    framework_files = load_framework_files()
    return {
        "files": list(framework_files.keys()),
        "count": len(framework_files),
        "directory": FRAMEWORK_DIR,
        "directory_exists": os.path.exists(FRAMEWORK_DIR),
        "root_directories": [d for d in os.listdir('.') if os.path.isdir(d)]
    }

@app.get("/files/{filename}")
async def get_file(filename: str):
    """
    Get a specific framework file by name
    """
    if not filename.endswith(".json"):
        filename += ".json"
    
    framework_files = load_framework_files()
    
    if filename not in framework_files:
        file_path = os.path.join(FRAMEWORK_DIR, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {filename} directly: {str(e)}")
        
        raise HTTPException(status_code=404, detail=f"File {filename} not found in {FRAMEWORK_DIR}")
    
    return framework_files[filename]

@app.get("/framework")
async def get_framework():
    """
    Get the complete framework data (all files combined)
    """
    framework_files = load_framework_files()
    
    if not framework_files:
        raise HTTPException(
            status_code=404, 
            detail=f"No framework files found in {FRAMEWORK_DIR}. Directory exists: {os.path.exists(FRAMEWORK_DIR)}. Root directories: {[d for d in os.listdir('.') if os.path.isdir(d)]}"
        )
    
    return framework_files

@app.post("/generate-review", response_model=ReviewResponse)
async def create_review(request: ReviewRequest):
    """
    Generate a product review using the framework and Claude
    """
    review = await generate_review(request)
    
    # Get the list of components used
    if not request.include_components:
        components_used = ["framework-config.json", "review-strategy.json", "content-structure.json"]
    else:
        components_used = [c if c.endswith(".json") else c + ".json" for c in request.include_components]
    
    return ReviewResponse(
        review=review,
        components_used=components_used
    )

# Create Gradio app with tabs for different functionalities
with gr.Blocks(title="Amazon Review Framework") as gradio_app:
    gr.Markdown("""# Amazon Review Framework
    Generate professional product reviews using the Amazon Review Framework with Claude.""")
    
    if not has_anthropic:
        gr.Markdown("⚠️ **Warning: Anthropic API key not set.** Please configure the ANTHROPIC_API_KEY environment variable to enable review generation.")
    
    with gr.Tabs():
        # Tab 1: Generate Review
        with gr.TabItem("Generate Review"):
            # Get list of available framework components
            framework_files = load_framework_files()
            component_choices = list(framework_files.keys())
            
            with gr.Row():
                with gr.Column():
                    product_name = gr.Textbox(label="Product Name", placeholder="Enter the product name")
                    product_category = gr.Textbox(label="Product Category", placeholder="E.g., Electronics, Kitchen, Beauty, etc.")
                    user_experience = gr.Textbox(
                        label="Your Experience with the Product", 
                        placeholder="Describe your experience with the product in detail...",
                        lines=10
                    )
                    components = gr.CheckboxGroup(
                        label="Framework Components to Include",
                        choices=component_choices,
                        info="Select the framework components to use for review generation"
                    )
                    submit_btn = gr.Button("Generate Review")
                    
                with gr.Column():
                    review_output = gr.Textbox(label="Generated Review", lines=20)
            
            submit_btn.click(
                fn=sync_generate_review,
                inputs=[product_name, product_category, user_experience, components],
                outputs=review_output
            )
        
        # Tab 2: File Explorer
        with gr.TabItem("File Explorer"):
            gr.Markdown("## Framework Files")
            
            framework_info = f"""
            Framework Directory: {FRAMEWORK_DIR}
            Directory exists: {os.path.exists(FRAMEWORK_DIR)}
            """
            
            if os.path.exists(FRAMEWORK_DIR):
                files = os.listdir(FRAMEWORK_DIR)
                json_files = [f for f in files if f.endswith('.json')]
                framework_info += f"""
                Total files in directory: {len(files)}
                JSON files found: {len(json_files)}
                JSON files: {', '.join(json_files)}
                """
            else:
                framework_info += "\nDirectory not found!"
                root_dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
                framework_info += f"\nAvailable directories at root: {', '.join(root_dirs)}"
            
            gr.Textbox(value=framework_info, label="Framework Directory Information", lines=10)
            
            # File system browser
            gr.Markdown("## File System Explorer")
            
            def list_directory(path="."):
                try:
                    items = os.listdir(path)
                    dirs = []
                    files = []
                    
                    for item in items:
                        full_path = os.path.join(path, item)
                        if os.path.isdir(full_path):
                            dirs.append(f"📁 {item}/")
                        elif item.endswith('.json'):
                            files.append(f"📄 {item} [JSON]")
                        else:
                            files.append(f"📄 {item}")
                    
                    return "\n".join(sorted(dirs) + sorted(files))
                except Exception as e:
                    return f"Error listing directory {path}: {str(e)}"
            
            dir_path = gr.Textbox(value=".", label="Directory Path")
            list_btn = gr.Button("List Directory")
            dir_contents = gr.Textbox(value=list_directory(), label="Directory Contents", lines=20)
            
            list_btn.click(fn=list_directory, inputs=dir_path, outputs=dir_contents)
        
        # Tab 3: File Viewer
        with gr.TabItem("File Viewer"):
            gr.Markdown("## Framework File Viewer")
            
            def get_framework_file(filename):
                if not filename.endswith(".json"):
                    filename += ".json"
                
                file_path = os.path.join(FRAMEWORK_DIR, filename)
                try:
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            return json.dumps(data, indent=2)
                    else:
                        return f"File {filename} not found in {FRAMEWORK_DIR}"
                except Exception as e:
                    return f"Error loading {filename}: {str(e)}"
            
            json_files = [] 
            if os.path.exists(FRAMEWORK_DIR):
                json_files = [f for f in os.listdir(FRAMEWORK_DIR) if f.endswith('.json')]
            
            file_selector = gr.Dropdown(choices=json_files, label="Select Framework File")
            view_btn = gr.Button("View File")
            file_contents = gr.Code(language="json", label="File Contents", lines=20)
            
            view_btn.click(fn=get_framework_file, inputs=file_selector, outputs=file_contents)

# Mount the Gradio app at /gradio
app = gr.mount_gradio_app(app, gradio_app, path="/gradio")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=True)