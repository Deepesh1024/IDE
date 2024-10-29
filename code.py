import streamlit as st
import subprocess
import tempfile
import os
from datetime import datetime

# Page configuration with custom theme
st.set_page_config(
    page_title="CodeCraft IDE",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
theme_color = "#333333"
st.markdown(f"""
    <style>
        .stApp {{
            max-width: 100%;
            background-color: {theme_color};
            color: #ffffff;
        }}
        .main {{
            padding: 1rem;
        }}
        .stTextArea textarea {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
        }}
        .output-container {{
            background-color: #f0f2f6;
            border-radius: 5px;
            padding: 1rem;
            margin-top: 1rem;
        }}
        .sidebar .stSelectbox {{
            margin-bottom: 1rem;
        }}
        .css-1d391kg {{
            padding-top: 1rem;
        }}
    </style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.image("https://api.dicebear.com/7.x/bottts/svg?seed=codecraft", width=100)
    st.title("CodeCraft IDE")
    
    # Language selection with icons
    language_options = {
        "Python": "🐍 Python",
        "JavaScript": "💛 JavaScript",
        "C": "⚡ C",
        "C++": "⚡ C++"
    }
    language = st.selectbox(
        "Select Language",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x]
    )
    
    # Additional settings
    auto_indent = st.checkbox("Auto-indent", value=True)
    show_line_numbers = st.checkbox("Show line numbers", value=True)
    
    st.markdown("---")
    st.markdown("### Quick Templates")
    
    # Template snippets based on selected language
    templates = {
        "Python": {
            "Hello World": 'print("Hello, World!")',
            "For Loop": "for i in range(5):\n    print(i)",
            "Function": "def greet(name):\n    return f'Hello, {name}!'"
        },
        "JavaScript": {
            "Hello World": 'console.log("Hello, World!");',
            "For Loop": "for (let i = 0; i < 5; i++) {\n    console.log(i);\n}",
            "Function": "function greet(name) {\n    return `Hello, ${name}!`;\n}"
        },
        "C": {
            "Hello World": '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}',
            "For Loop": '#include <stdio.h>\n\nint main() {\n    for(int i = 0; i < 5; i++) {\n        printf("%d\\n", i);\n    }\n    return 0;\n}',
            "Function": '#include <stdio.h>\n\nvoid greet(char* name) {\n    printf("Hello, %s!\\n", name);\n}'
        },
        "C++": {
            "Hello World": '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
            "For Loop": '#include <iostream>\n\nint main() {\n    for(int i = 0; i < 5; i++) {\n        std::cout << i << std::endl;\n    }\n    return 0;\n}',
            "Function": '#include <iostream>\n\nvoid greet(std::string name) {\n    std::cout << "Hello, " << name << "!" << std::endl;\n}'
        }
    }
    
    selected_template = st.selectbox("Load Template", [""] + list(templates[language].keys()))
    if selected_template:
        st.session_state.code = templates[language][selected_template]

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Code Editor")
    
    # Initialize session state for code if not exists
    if 'code' not in st.session_state:
        st.session_state.code = ""
    
    # Code editor with custom styling
    code = st.text_area(
        "Code Editor",
        value=st.session_state.code,
        height=400,
        key="code_editor"
    )

    # Action buttons
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        run_button = st.button("▶️ Run Code", use_container_width=True)
    with col1_2:
        save_button = st.button("💾 Save Code", use_container_width=True)

    if save_button:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extensions = {
            "Python": "py",
            "JavaScript": "js",
            "C": "c",
            "C++": "cpp"
        }
        filename = f"code_{now}.{file_extensions[language]}"
        st.download_button(
            label="Download Code",
            data=code,
            file_name=filename,
            mime="text/plain"
        )

with col2:
    st.markdown("### Output")
    output_container = st.empty()
    
    if run_button and code.strip():
        with st.spinner("Running code..."):
            if language == "Python":
                with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
                    temp_file.write(code.encode("utf-8"))
                    temp_file.flush()
                    file_path = temp_file.name

                try:
                    result = subprocess.run(["python", file_path], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        output_container.success(result.stdout)
                    else:
                        output_container.error(result.stderr)
                except subprocess.TimeoutExpired:
                    output_container.error("Execution timed out (5 seconds limit)")
                finally:
                    os.remove(file_path)

            elif language == "JavaScript":
                with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as temp_file:
                    temp_file.write(code.encode("utf-8"))
                    temp_file.flush()
                    file_path = temp_file.name

                try:
                    result = subprocess.run(["node", file_path], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        output_container.success(result.stdout)
                    else:
                        output_container.error(result.stderr)
                except subprocess.TimeoutExpired:
                    output_container.error("Execution timed out (5 seconds limit)")
                finally:
                    os.remove(file_path)

            elif language in ["C", "C++"]:
                compiler = "gcc" if language == "C" else "g++"
                file_extension = ".c" if language == "C" else ".cpp"
                
                with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
                    temp_file.write(code.encode("utf-8"))
                    temp_file.flush()
                    file_path = temp_file.name
                    output_file = tempfile.NamedTemporaryFile(delete=False).name

                try:
                    compile_result = subprocess.run(
                        [compiler, file_path, "-o", output_file],
                        capture_output=True,
                        text=True
                    )
                    if compile_result.returncode == 0:
                        try:
                            run_result = subprocess.run(
                                [output_file],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            if run_result.returncode == 0:
                                output_container.success(run_result.stdout)
                            else:
                                output_container.error(run_result.stderr)
                        except subprocess.TimeoutExpired:
                            output_container.error("Execution timed out (5 seconds limit)")
                    else:
                        output_container.error(f"Compilation Error:\n{compile_result.stderr}")
                finally:
                    os.remove(file_path)
                    if os.path.exists(output_file):
                        os.remove(output_file)
    
    # Documentation and tips
    with st.expander("📚 Documentation & Tips"):
        st.markdown(f"""
        ### Quick Reference for {language}
        
        {"Click on the templates to load sample code!"}
        
        **Python:**
        - Use `print()` for output
        - Import modules using `import`
        
        **JavaScript:**
        - Use `console.log()` for output
        - Define functions using `function`
        
        **C/C++:**
        - Use `printf()` for output (C) and `std::cout` for C++
        - Include headers with `#include`
        """)

# Run the app with the following command:
# streamlit run your_script_name.py
