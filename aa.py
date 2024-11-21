import matplotlib.pyplot as plt
import re

def execute_command(command, dataframes, st):
    try:
        # Store intermediate results
        intermediate_results = []
        
        # Split command into individual statements
        statements = [s.strip() for s in command.split('\n') if s.strip()]
        
        # Initialize execution environment
        exec_globals = {"st": st, "plt": plt, "np": np}
        exec_globals.update(dataframes)
        exec_locals = {}
        
        # Execute each statement and capture output
        for statement in statements:
            if statement:
                try:
                    # Execute single statement
                    exec(statement, exec_globals, exec_locals)
                    
                    # Capture any potential output
                    if 'result' in exec_locals:
                        intermediate_results.append(exec_locals['result'])
                    elif '_' in exec_locals and exec_locals['_'] is not None:
                        intermediate_results.append(exec_locals['_'])
                except Exception as step_error:
                    # Log the error but continue execution
                    print(f"Step error: {step_error}")
                    continue
        
        # Determine final output
        if intermediate_results:
            # Format the results based on type
            formatted_results = []
            for result in intermediate_results:
                if isinstance(result, (pd.DataFrame, pd.Series)):
                    formatted_results.append(result.to_string())
                elif isinstance(result, (list, dict, set)):
                    formatted_results.append(str(result))
                else:
                    formatted_results.append(str(result))
            
            return "\n\n".join(formatted_results)
        else:
            return exec_locals.get('output', "Execution completed but no explicit output captured.")
            
    except Exception as e:
        return f"Error executing command: {e}"

def process_query_response(query_response, dataframes, st):
    # Extract code blocks if present
    code_blocks = re.findall(r'```python\n(.*?)\n```', query_response, re.DOTALL)
    
    if code_blocks:
        results = []
        for code in code_blocks:
            result = execute_command(code, dataframes, st)
            if result:
                results.append(result)
        
        # Format and display results in Streamlit
        with st.chat_message("R"):
            for idx, result in enumerate(results):
                st.write(f"Result {idx + 1}:")
                st.write(result)
                st.markdown("---")
    else:
        # Execute as single block if no code blocks found
        result = execute_command(query_response, dataframes, st)
        with st.chat_message("R"):
            st.write(result)
