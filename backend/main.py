from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from .ast_compare import compare_code
    from .graphviz_utils import ast_to_dot
    from .semantics import analyze_semantics  # Changed from semantic to semantics
    from .parser import parse_code
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required files are in the same directory")

app = FastAPI(title="Code Plagiarism Detector API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeComparisonRequest(BaseModel):
    code1: str
    code2: str

class SemanticAnalysisRequest(BaseModel):
    code: str

@app.get("/")
async def root():
    return {"message": "Code Plagiarism Detector API", "version": "1.0.0"}

@app.post("/api/compare")
async def compare_code_snippets(request: CodeComparisonRequest):
    try:
        result = compare_code(request.code1, request.code2)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # Convert ASTs to DOT format if they exist
        dot1 = ast_to_dot(result['ast1'], "AST1") if result['ast1'] else "// No AST generated"
        dot2 = ast_to_dot(result['ast2'], "AST2") if result['ast2'] else "// No AST generated"
        
        return {
            "similarity": result['similarity'],
            "ast1": dot1,
            "ast2": dot2,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error analyzing code: {str(e)}")

@app.post("/api/semantic")
async def analyze_code_semantics(request: SemanticAnalysisRequest):
    try:
        ast = parse_code(request.code)
        result = analyze_semantics(ast)
        
        return {
            "errors": result['errors'],
            "warnings": result['warnings'],
            "symbol_table": result['symbol_table'],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error in semantic analysis: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Code Plagiarism Detector API...")
    print("Access the API at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)