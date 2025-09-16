import time
import re
import json
import ast
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import os
# Resume from last run flag
RESUME = 1
# Include context flag
CONTEXT = 1
# Output directory
OUTPUT_DIR = "Python/Non-Zero/hybrid"
# Execution Timeout time, 
TIMEOUT = 1200
read_mode = "a+"
prompt_template = """
You are a Python software engineer.

Generate Python code based on the following function signature and docstring. 
Output ONLY the code generated, in python markdown format. /think 
## Tips
- You should follow a test-driven development approach, first generating comprehensive unit tests before writing the actual code.
{input}

{context}
"""
client = OpenAI(
    api_key="EMPTY",
    base_url="http://0.0.0.0:4567/v1",   # vLLM's OpenAI-compatible server
)
def call_model(prompt, model_name, options):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        **options
    )
    return response
def extract_function_signature(code_string):
    """
    Extracts function signatures from Python code string.

    Parameters:
        code_string (str): Python code as string.

    Returns:
        List[str]: List of function signatures like 'def func(arg1, arg2)'.
    """
    signatures = []
    try:
        parsed = ast.parse(code_string)
        for node in parsed.body:
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                args = [arg.arg for arg in node.args.args]
                if node.args.vararg:
                    args.append('*' + node.args.vararg.arg)
                if node.args.kwarg:
                    args.append('**' + node.args.kwarg.arg)
                signature = f"def {func_name}({', '.join(args)})"
                if node.returns:
                    try:
                        signature += f" -> {ast.unparse(node.returns)}"
                    except AttributeError:
                        pass  
                signatures.append(signature)
    except SyntaxError:
        print("Error in parsing signature")
        return []  
    return signatures

def extract_code_from_markers(text):
    start_pattern = r"@+\s*generated code\s*@+"
    end_pattern = r"@+\s*end of code\s*@+"

    start_match = re.search(start_pattern, text, re.IGNORECASE)
    end_match = re.search(end_pattern, text, re.IGNORECASE)

    if start_match and end_match:
        start_index = start_match.end()
        end_index = end_match.start()
        raw_code = text[start_index:end_index].strip()
    elif start_match:
        raw_code = text[start_match.end():].strip()
    elif end_match:
        raw_code = text[:end_match.start()].strip()
    else:
        raw_code = text.strip()
    return raw_code


_at_line_pattern = re.compile(r"^\s*@\s?", re.MULTILINE)




def executeExperiment(input_file, main_dir, model_name = "deepseek-r1", mode=1):
    global_start_time = time.time()
    os.makedirs(f"{main_dir}",exist_ok=True)
    if not RESUME:
        open(f"{main_dir}/Qwen-14Bvllm.jsonl", "w", encoding="utf-8").close()
    with open(input_file, "r", encoding="utf-8") as dataset_file,\
    open(f"{main_dir}/Qwen-14Bvllm.jsonl", read_mode, encoding="utf-8") as allJson:
        records = []
        for line in dataset_file:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            records.append(d)
        options = {'temperature': 0} if not mode else {}
        if RESUME:
            allJson.seek(0)
            print("Loading previous run")
            ids_done = []
            print(f"Total previous entries: {sum(1 for _ in allJson)}")
            allJson.seek(0)
            for line in allJson:
                data = ast.literal_eval(line.strip()) 
                if '_id' in data:
                    ids_done.append(data['_id'])  
            if ids_done:
                print("Loaded previous run")
        for record in records:
            id = record['question_id']
            input = record['input']
            if RESUME:
                if id in ids_done:
                    print(f"ID {id} was once executed")
                    continue
                else:
                    print(f"Working on ID: {id}")
            else:
                print(f"Working on ID: {id}")
            start_time = time.time()
            context_str = ''
            if CONTEXT:
                with open("CoderEval4Python.json", "r", encoding='utf-8') as context:
                    d = json.load(context)
                    for record in d.get("RECORDS"):
                        if record.get("_id") == id:
                            context_str = record.get("all_context", "{}")
                            context_str= json.loads(context_str)
                            packages = context_str["import"]
                            packages = " ".join(dict.fromkeys(packages.split()))
                            context_str = f"### Context\nImported Packages: {packages}\nWithin file: {context_str['file']}\nWithin class: {context_str['class']}"

            prompt = prompt_template.format(input=input, context=context_str if context_str else "")
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(call_model, prompt, model_name, options)
                    response = future.result(timeout=TIMEOUT)  
            except TimeoutError:
                print(f"Timeout while processing ID {id}, retrying....")
                
                try:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(call_model, prompt, model_name, options)
                        response = future.result(timeout=TIMEOUT/2) 
                except TimeoutError:
                    print(f"Timeout while processing ID {id}, skipping....")
                    continue  # Skip to next record
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time taken to get response: {elapsed_time:.4f} seconds")
            model_dir = "qwen314"
            os.makedirs(f"{main_dir}/{model_dir}Reasoningvllm",exist_ok=True)
            os.makedirs(f"{main_dir}/{model_dir}IndivOutputvllm",exist_ok=True)
            os.makedirs(f"{main_dir}/{model_dir}CleanedOutputvllm",exist_ok=True)
            with open(f"{main_dir}/{model_dir}Reasoningvllm/{id}.txt","w", encoding="utf-8") as reasoningFile, \
                open(f"{main_dir}/{model_dir}IndivOutputvllm/{id}.txt", "w", encoding="utf-8") as outFile,\
                open(f"{main_dir}/{model_dir}CleanedOutputvllm/{id}.txt", "w", encoding="utf-8")as cleanOut:
                reasoning = response.choices[0].message.reasoning_content                        
                reasoning = reasoning if reasoning else ""
                reasoningFile.write(reasoning)
                # Get the answer after the </think> tag
                answer = response.choices[0].message.content
                outFile.write(answer)
                # Cleaning
                # Filter for markdown
                code_block = re.search(r"```(?:python)?\n?(.*?)```", answer, re.DOTALL | re.IGNORECASE)
                if code_block:
                    answer = code_block.group(1).strip()
                # Extract the code
                final_code = extract_code_from_markers(answer)
                cleanOut.write(final_code)
                output_json = {
                "_id": id,
                "generate_results": [final_code],
                "prompt": prompt,
                }
                allJson.seek(0,2)
                allJson.write(json.dumps(output_json) + "\n")
                print("Done Writing")
                allJson.flush()
executeExperiment("CEPythonHumanLabel.jsonl", OUTPUT_DIR,model_name="Qwen/Qwen3-14B", mode=1)
