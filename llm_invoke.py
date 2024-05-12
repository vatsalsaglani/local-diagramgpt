from llama_cpp import Llama
from typing import List, Dict, Union
from ctx import ContextManagement
import traceback


class LLM:

    def __init__(self, model_path: str, **kwargs):
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=kwargs.get("n_gpu_layers",
                                    -1),  # Uncomment to use GPU acceleration
            seed=kwargs.get("seed", 1337),  # Uncomment to set a specific seed
            n_ctx=kwargs.get("n_ctx",
                             4096),  # Uncomment to increase the context window
            n_threads=kwargs.get("n_threads", 4),
            verbose=False,
        )
        self.ctx = ContextManagement(5300)

    def __stream__(self, messages: List[Dict], **kwargs):
        try:
            input_message = self.ctx(messages)
            # print("INPUT MESSAGE: \n", input_message, "\n")
            # exit()
            output = self.llm(input_message, stream=True, echo=False, **kwargs)
            for op in output:
                yield op.get("choices")[0].get("text") or ""
        except Exception as err:
            print(f"EXCEPTION: {str(err)}\nTraceback:\n")
            print(traceback.format_exc())
            raise Exception(err)

    def __complete__(self, messages: List[Dict], **kwargs):
        input_message = self.ctx(messages)
        output = self.llm(input_message, echo=False, **kwargs)
        return output.get("choices")[0].get("text")
