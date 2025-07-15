import os

import openai
from dotenv import load_dotenv
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.messages import HumanMessage
from langchain_openai import \
    AzureChatOpenAI  # Import AzureChatOpenAI from LangChain for Azure OpenAI


class LLM_Mgr:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Get credentials from environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        # Validate that all required credentials are present
        if not all([api_key, azure_endpoint, deployment]):
            raise ValueError(
                "Missing required Azure OpenAI credentials. Please set: "
                "AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT"
            )

        openai.api_key = api_key  # Set OpenAI API key globally for openai library
        self.llm = AzureChatOpenAI(  # Initialize AzureChatOpenAI client
            azure_endpoint=azure_endpoint,
            openai_api_key=api_key,
            openai_api_version=api_version,
            deployment_name=deployment,
            temperature=0.7,  # LLM temperature for response randomness
            max_tokens=4000,  # Maximum tokens for response
            streaming=True,  # Enable streaming output
            callbacks=[StreamingStdOutCallbackHandler()],
            verbose=True,
        )

    def improve_sfc2(
        self,
        sfc1,
        sfc2,
        unmatched_paths,
        # This file contain the prompt template
        prompt_template_path="iterative_prompting.txt",
        prompt_path="prompt_refiner.txt",
        # Initially it is same as prompt_template_path
        # But after the LLM response, it will be updated with the new prompt
        sfc2_path="dec2hex_mod.txt",  # Path to save the improved SFC2 code
    ):
        if not unmatched_paths:  # Early exit if there are no unmatched paths to improve
            print("No unmatched paths to improve on.")
            return False

        # Prepare the header for unmatched paths table in the prompt
        table_lines = ["From\tTo\tTransitions\tZ3 Condition\tZ3 Data Transformation"]
        for p in unmatched_paths:  # Loop through each unmatched path and build a row
            row = [
                str(p.get("from", "")),  # From step
                str(p.get("to", "")),  # To step
                str(p.get("transitions", "")),  # Transition(s)
                str(p.get("cond", "")),  # Z3 condition
                str(p.get("subst", "")),  # Z3 data transformation
            ]
            table_lines.append("\t".join(row))  # Add the row to the table
        # Join all rows for the prompt
        non_equiv_paths_str = "\n".join(table_lines)

        # Prepare SFC2 and SFC1 step/transition code strings for the prompt
        sfc2_code = (
            f"steps2 = {repr(sfc2.steps)}\ntransitions2 = {repr(sfc2.transitions)}"
        )
        sfc1_code = (
            f"steps1 = {repr(sfc1.steps)}\ntransitions1 = {repr(sfc1.transitions)}"
        )

        # Read the interative_prompting.txt  file
        with open(prompt_template_path, "r") as f:
            prompt_template = f.read()

        # Fill the template with the current iteration's data
        prompt = prompt_template.format(
            non_equiv_paths_str=non_equiv_paths_str,
            sfc2_code=sfc2_code,
            sfc1_code=sfc1_code,
        )

        # Save the completed prompt (with all placeholders filled) to a file for reproducibility and debugging
        with open(prompt_path, "w") as f:
            f.write(prompt)
        print(f"Saved LLM prompt to {prompt_path}")

        # Send the prompt to the LLM and get the response
        llm_response = self.improve_sfc(prompt)
        print("=== LLM OUTPUT ===")
        print(llm_response)  # Print the model's response
        print("==================")

        # Save the model's response to a file for checking and debugging
        with open("llm_response.txt", "w") as f:
            f.write(llm_response)

        # Extract the code block (steps2, transitions2) from the LLM response
        code_block = self.extract_code_block(llm_response)
        if not code_block:
            print("No valid code block found in LLM output.")
            return False
        try:
            # Execute the extracted code to get updated steps2 and transitions2
            steps2, transitions2 = self.sfc2_code_to_python(code_block)
        except Exception as e:  # Handle code parsing errors
            print(f"Error parsing LLM output: {e}")
            return False

        # Helper function to format a list of dicts as Python code
        def format_list_of_dicts(name, lst):
            lines = [f"{name} = ["]
            for idx, obj in enumerate(lst):
                comma = "," if idx < len(lst) - 1 else ""
                items = []
                for k, v in obj.items():
                    if isinstance(v, str):
                        items.append(f'"{k}": "{v}"')  # String value
                    else:
                        items.append(f'"{k}": {repr(v)}')  # Non-string value
                lines.append("        {" + ", ".join(items) + "}" + comma)
            lines.append("    ]\n")
            return "\n".join(lines)

        # Take it from stackoverflow.com/questions/70618695/how-to-format-a-list-of-dictionaries-as-python-code

        # Helper function to format a list as Python code
        def format_list(name, lst):
            vals = ", ".join(f'"{v}"' for v in lst)
            return f"{name} = [{vals}]\n"

        # Helper function to format a string assignment
        def format_string(name, value):
            return f'{name} = "{value}"\n'

        # Save the improved SFC2 to file for the next iteration
        with open(sfc2_path, "w") as f:
            f.write(format_list_of_dicts("steps", steps2))
            f.write(format_list_of_dicts("transitions", transitions2))
            f.write(format_list("variables", sfc2.variables))
            f.write(format_string("initial_step", sfc2.initial_step))
        print(f"Updated SFC2 saved to {sfc2_path}")

        return True  # Indicate that improvement was successfully applied

    def improve_sfc(self, prompt):
        # Send the prompt to the LLM and get response
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content  # Return LLM response as string

    @staticmethod
    def extract_code_block(llm_output):
        import re  # Import regular expressions module

        # Try to find a Python code block in the LLM output
        match = re.search(r"```(?:python)?\s*([\s\S]*?)```", llm_output)
        if match:
            return match.group(1)  # Return code inside code block
        # Fallback: collect lines starting with 'steps2' or 'transitions2'
        lines = []
        for line in llm_output.splitlines():
            if line.strip().startswith("steps2") or line.strip().startswith(
                "transitions2"
            ):
                lines.append(line)
        result = "\n".join(lines)
        return result if result.strip() else None

    @staticmethod
    def sfc2_code_to_python(sfc2_code_str):
        local_vars = {}  # Create a dict for local variables
        # Execute the code string in a restricted namespace
        exec(sfc2_code_str, {}, local_vars)
        # Return the extracted values
        return local_vars["steps2"], local_vars["transitions2"]
