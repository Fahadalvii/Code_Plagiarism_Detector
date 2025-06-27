import streamlit as st
import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    st.warning("Graphviz not installed. Install with: pip install graphviz")

try:
    from backend.ast_compare import compare_code, calculate_similarity
    from backend.parser import parse_code
    from backend.semantic import analyze_semantics  # Changed from semantic to semantics
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Make sure all required files are in the same directory")
    st.stop()

def ast_to_graphviz(ast, graph_name="AST"):
    """Convert AST to Graphviz DOT format for Streamlit"""
    if not GRAPHVIZ_AVAILABLE:
        return None
    
    if ast is None:
        dot = graphviz.Digraph(name=graph_name)
        dot.node('empty', 'Empty AST')
        return dot
    
    dot = graphviz.Digraph(name=graph_name)
    dot.attr('node', shape='box')
    
    def add_nodes_edges(node, parent_id=None):
        if node is None:
            return
        
        node_id = str(id(node))
        label = str(node.type) if hasattr(node, 'type') else 'Unknown'
        if hasattr(node, 'value') and node.value is not None:
            label += f"\n{node.value}"
        dot.node(node_id, label)
        
        if parent_id is not None:
            dot.edge(parent_id, node_id)
        
        if hasattr(node, 'children'):
            for child in node.children:
                add_nodes_edges(child, node_id)
    
    add_nodes_edges(ast)
    return dot

def display_similarity_score(similarity):
    """Display similarity score with appropriate color coding"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric("Similarity Score", f"{similarity:.2f}%")
        
        # Color-coded similarity interpretation
        if similarity >= 80:
            st.error("⚠️ High Similarity - Potential Plagiarism")
        elif similarity >= 60:
            st.warning("⚠️ Moderate Similarity - Needs Review")
        elif similarity >= 40:
            st.info("ℹ️ Some Similarity - Likely Different")
        else:
            st.success("✅ Low Similarity - Likely Original")
    
    return similarity

def main():
    st.set_page_config(layout="wide", page_title="Plagiarism Detector")
    st.title("🔍 Code Plagiarism Detector")
    st.markdown("Analyze code similarity using Abstract Syntax Trees (AST)")
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Code Comparison", "Semantic Analysis", "About"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Code Snippet 1")
            code1 = st.text_area("Enter first code snippet:", height=300, 
                                 value="int a = 5;\nint b = a + 3;\nif (b > 7) {\n    int c = b * 2;\n}",
                                 key="code1")
        
        with col2:
            st.subheader("Code Snippet 2")
            code2 = st.text_area("Enter second code snippet:", height=300, 
                                 value="int x = 5;\nint y = x + 3;\nif (y > 7) {\n    int z = y * 2;\n}",
                                 key="code2")
        
        if st.button("🔍 Compare Code", type="primary"):
            if not code1.strip() or not code2.strip():
                st.error("Please enter code in both text areas.")
                return
            
            with st.spinner("Analyzing code similarity..."):
                try:
                    # Parse and compare code
                    result = compare_code(code1, code2)
                    
                    if 'error' in result:
                        st.error(f"Error: {result['error']}")
                        return
                    
                    similarity = result['similarity']
                    ast1 = result['ast1']
                    ast2 = result['ast2']
                    
                    # Display similarity score
                    display_similarity_score(similarity)
                    
                    # Display ASTs if graphviz is available
                    if GRAPHVIZ_AVAILABLE:
                        st.subheader("Abstract Syntax Trees")
                        ast_col1, ast_col2 = st.columns(2)
                        
                        with ast_col1:
                            st.write("**AST for Code Snippet 1**")
                            try:
                                dot1 = ast_to_graphviz(ast1, "AST1")
                                if dot1:
                                    st.graphviz_chart(dot1.source)
                                else:
                                    st.info("No AST generated for code snippet 1")
                            except Exception as e:
                                st.error(f"Error generating AST visualization: {e}")
                        
                        with ast_col2:
                            st.write("**AST for Code Snippet 2**")
                            try:
                                dot2 = ast_to_graphviz(ast2, "AST2")
                                if dot2:
                                    st.graphviz_chart(dot2.source)
                                else:
                                    st.info("No AST generated for code snippet 2")
                            except Exception as e:
                                st.error(f"Error generating AST visualization: {e}")
                    else:
                        st.info("Install graphviz to see AST visualizations: pip install graphviz")
                        
                except Exception as e:
                    st.error(f"Error analyzing code: {str(e)}")
                    st.info("Please check your code syntax and try again.")
    
    with tab2:
        st.subheader("Semantic Analysis")
        st.markdown("Analyze individual code snippets for semantic issues")
        
        code_to_analyze = st.text_area("Enter code to analyze:", height=200,
                                      value="int a = 5;\nint b;\nint c = a + b;",
                                      key="semantic_code")
        
        if st.button("🔍 Analyze Semantics"):
            if not code_to_analyze.strip():
                st.error("Please enter code to analyze.")
                return
            
            with st.spinner("Performing semantic analysis..."):
                try:
                    ast = parse_code(code_to_analyze)
                    semantic_result = analyze_semantics(ast)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Errors")
                        if semantic_result['errors']:
                            for error in semantic_result['errors']:
                                st.error(f"❌ {error}")
                        else:
                            st.success("✅ No semantic errors found")
                    
                    with col2:
                        st.subheader("Warnings")
                        if semantic_result['warnings']:
                            for warning in semantic_result['warnings']:
                                st.warning(f"⚠️ {warning}")
                        else:
                            st.info("ℹ️ No warnings")
                    
                    st.subheader("Symbol Table")
                    if semantic_result['symbol_table']:
                        # Convert symbol table to display format
                        symbol_data = []
                        for var_name, info in semantic_result['symbol_table'].items():
                            symbol_data.append({
                                'Variable': var_name,
                                'Type': info.get('type', 'Unknown'),
                                'Scope': info.get('scope', 'Unknown'),
                                'Used': info.get('used', False),
                                'Initialized': info.get('initialized', False)
                            })
                        st.table(symbol_data)
                    else:
                        st.info("No symbols found")
                        
                except Exception as e:
                    st.error(f"Error in semantic analysis: {str(e)}")
    
    with tab3:
        st.subheader("About")
        st.markdown("""
        This Code Plagiarism Detector uses Abstract Syntax Trees (AST) to analyze code similarity.
        
        **Features:**
        - Parse code into AST representation
        - Compare AST structures for similarity detection
        - Semantic analysis for code validation
        - Interactive visualization of ASTs
        
        **How it works:**
        1. Code is tokenized and parsed into an AST
        2. ASTs are normalized to handle variable name differences
        3. Tree edit distance is calculated between normalized ASTs
        4. Similarity score is computed based on structural differences
        """)

if __name__ == "__main__":
    main()