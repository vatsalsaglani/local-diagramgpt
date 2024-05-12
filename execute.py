import ast
import io
import sys
import traceback


def extract_python_code(text):
    """
    Extracts Python code from a Markdown-formatted text block.

    Args:
    text (str): A string containing Markdown-formatted text.

    Returns:
    str: The extracted Python code.
    """
    # Start extracting when finding the opening ```python
    start_code = text.find("```python")
    if start_code == -1:
        return "No Python code block found."

    # Adjust the start to the actual beginning of the code after ```python
    start_code += len("```python")

    # Find the closing ``` which marks the end of the Python code block
    end_code = text.find("```", start_code)
    if end_code == -1:
        return "No closing tag for Python code block."

    # Extract the code by slicing from start_code to end_code
    code = text[start_code:end_code].strip()
    return code


def relay(msg):
    sys.__stdout__.write(msg + "\n")


def executeCodeBlock(content: str):
    code_block = extract_python_code(content)
    parsed = ast.parse(code_block)

    for node in parsed.body:
        line = code_block.splitlines()[node.lineno - 1].strip()

        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            if isinstance(node, ast.Expr):
                value = eval(
                    compile(ast.Expression(node.value), "<string>", "eval"))
                output = new_stdout.getvalue().strip(
                )  # Get the output from new_stdout
                yield {
                    "code": line,
                    "output": value if value else output,
                }  # Use value if it's not None, else use output
                continue  # go to next iteration
            exec(
                compile(ast.Module(body=[node], type_ignores=[]), "<string>",
                        "exec"))
            output = new_stdout.getvalue().strip(
            )  # Get the output from new_stdout
            if output:
                yield {"code": line, "output": output}

        except Exception as err:
            yield {
                "code": line,
                "error": str(err),
                "traceback": traceback.format_exc()
            }

        finally:
            sys.stdout = old_stdout  # Restore the original stdout
