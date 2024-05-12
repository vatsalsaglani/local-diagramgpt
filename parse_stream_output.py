import os
import json


def parse_function_call(content):
    try:
        function_call_data = json.loads(content)
        return function_call_data
    except json.JSONDecodeError:
        return None


def process_streaming_output(stream_generator):
    in_function_call = False
    buffer = ""
    function_calls = []
    tag_start = "<functioncall>"
    tag_end = "</functioncall>"
    content_op = ""

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

    # console.print(f"\nFUNCTIONS: \n {json.dumps(function_calls, indent=4)}")
    return function_calls, content_op
