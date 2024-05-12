import random
import os
import json
from llm_invoke import LLM
from search_tool import find_file_contains
# from parse_stream_output import process_streaming_output
from execute import executeCodeBlock
from prompts import *

from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "error": "bold red",
    "prompt": "dim cyan",
    "user_input": "bold green",
    "assistant": "bold blue",
})
console = Console(theme=custom_theme)

llm = LLM("./model/Meta-Llama-3-8B-Instruct-IQ3_M.gguf", n_ctx=6000)


def create_image_path():
    s = '1234567890'
    img_name = ''.join(random.sample(list(s), 5))
    img_name = f"static/{img_name}"
    return img_name


def parse_function_call(content):
    console.print(f"\nFunction: \n {content}\n", style="info")
    try:
        function_call_data = json.loads(content)
        return function_call_data
    except json.JSONDecodeError:
        return None


def diagramGPT(user_description: str):
    messages = [{
        "role": "system",
        "content": f"{SYSTEM_PROMPT_GRAPH_AND_IMAGES}",
    }, {
        "role": "user",
        "content": f"**User Description**: {user_description}"
    }]
    in_function_call = False
    buffer = ""
    function_calls = []
    tag_start = "<functioncall>"
    tag_end = "</functioncall>"
    content_op = ""
    stream_generator = llm.__stream__(messages, temperature=0.2, max_tokens=-1)

    for chunk in stream_generator:
        buffer += chunk
        while True:
            if in_function_call:
                # Check for the closing tag
                end_tag_index = buffer.find(tag_end)
                if end_tag_index != -1:
                    # Process the complete function call
                    function_call_content = buffer[:end_tag_index].strip()
                    if function_call_content:
                        function_calls.append(
                            parse_function_call(function_call_content))
                    # Reset buffer after the function call
                    buffer = buffer[end_tag_index + len(tag_end):]
                    in_function_call = False
                else:
                    # Need more chunks to complete the function call
                    break
            else:
                # Check for the starting tag
                start_tag_index = buffer.find(tag_start)
                if start_tag_index != -1:
                    # Print everything before the function call starts
                    # print_output(buffer[:start_tag_index])
                    yield buffer[:start_tag_index]

                    content_op += buffer[:start_tag_index]
                    # Update buffer to start after the opening tag
                    buffer = buffer[start_tag_index + len(tag_start):]
                    in_function_call = True
                else:
                    # If no starting tag and not inside a function call, print and clear buffer
                    if len(buffer) > len(tag_start):
                        # Print buffer except for the last part where a tag could start
                        # print_output(buffer[:-len(tag_start)])
                        yield buffer[:-len(tag_start)]
                        content_op += buffer[:-len(tag_start)]
                        buffer = buffer[-len(tag_start):]
                    break

    # If anything is left in the buffer after all chunks are processed, print it
    if buffer and not in_function_call:
        # print_output(buffer)
        yield buffer

    yield "\n"

    content_op += "\n**Selected Image Resources:** \n"

    for call in function_calls:
        if call:
            parameters = call.get("parameters")
            q = parameters.get("q")
            fp = find_file_contains("./resources", q)
            content_op += f"- Selected '{fp}' for `{q}`\n"

    img_path = create_image_path()

    messages = [{
        "role": "system",
        "content": GRAPH_GENERATION_PROMPT
    }, {
        "role":
        "user",
        "content":
        f"**User Description:** '{user_description}'\n**Path:** {img_path}\n{content_op}"
    }]

    for chunk in llm.__stream__(messages, temperature=0.5, max_tokens=-1):
        content_op += chunk
        yield chunk

    for output in executeCodeBlock(content_op):
        if not "error" in output:
            # relay(
            #     f'Executed: {output.get("code")} and got value: {output.get("output")}'
            # )
            continue
        else:
            # relay(
            #     f'Error executing {output.get("code")}.\nException: {output.get("error")}\nTraceback: {output.get("traceback")}'
            # )
            raise Exception("Error executing code")
    yield "\n\n"
    # img_path = os.path.join(os.getcwd(), f'{img_path}.png')
    yield f'!["Architecture"](./app/{img_path}.png)'


if __name__ == "__main__":

    user_description = str(console.input(f"What do you want to create?\n>>"))
    for chunk in diagramGPT(user_description):
        console.print(chunk, end="", style="assistant")
