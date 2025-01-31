
import json
from analyzers.model import AnalysisResult
import boto3
from botocore.exceptions import ClientError
from config import config



def fix_corrections(input_file: str, output_file: str, violations: AnalysisResult):
    
    """
    This function takes an input file path, output file path, and a list of violations as input.
    It processes each violation by:
    1. Grouping violations by rule
    2. Identifying impacted lines for each rule
    3. Generating fixes using Bedrock AI model
    4. Applying the fixes incrementally to create a corrected version
    Finally saves the corrected code to the output file path.

    Args:
        input_file (str): Path to the source file that needs fixing
        output_file (str): Path where the corrected file should be saved  
        violations (AnalysisResult): Object containing the violations to fix
    """
    
    
    # Source file
    source_file = ""
    with open(input_file, 'r') as f:
        source_file = f.read()

    print("Fixing violations")
    
    #Group the violations by rule name
    violations_by_rule = {}
    for violation in violations.violations:
        if violation.rule not in violations_by_rule:
            violations_by_rule[violation.rule] = []
        violations_by_rule[violation.rule].append(violation)
    
    # For each rule we launch bedrock
    for rule, violations in violations_by_rule.items():
        print(f"Fixing violations for rule: {rule}")
        try:       
            # Get the list of lines impacted by the violation.
            impacted_lines = set()
            for violation in violations:
                for i in range(violation.line_start, violation.line_end + 1):
                    impacted_lines.add(i)

            sys_instructions = """
            You are an experimented Java developer focused on Clean code and concise with efficient code fixes through pull requests. No additional comment. You do not add notes.
            """
            
            # Generate incremental patches for each violation
            prompt = f"""
Your task is to fix the violation to be conform with the rule "{violation.rule}" in the Java file passed as an attachment
The recommendation to fix the issue are : {violation.description} and the documentation is {violation.url}.

The output should be a Java source file that contains the minimum of modifications to fix the issue and keep the rest of the file untouched.
            
No additional explanations or Notes unless you write them as a Java comment and provided as it.

Impacted lines : {impacted_lines}


{source_file}
"""

            #Save prompt into a file
            with open("prompt.txt", "w") as f:
                f.write(prompt)
            
            # Apply the patches to the file
            refactored_file = call_bedrock(sys_instructions, prompt)
            
            # Remote markdown code blocks
            refactored_file = refactored_file.replace("```java", "").replace("```", "")
            
            source_file = refactored_file
        except Exception as e:
            print(f"Error while fixing violation: {e}")
            continue
    # write the last version in output_file
    with open(output_file, 'w') as f:
        f.write(source_file)


def call_bedrock(system_prompt: str, prompt: str) -> str: 
    """
    This function takes system and user prompts and calls the Bedrock API to generate a response.
    It configures the model parameters from config, formats the request with the prompts,
    calls the Bedrock runtime API, and returns the generated text response.

    Args:
        system_prompt (str): The system instructions for the model
        prompt (str): The user prompt/query for the model
        
    Returns:
        str: The generated text response from the Bedrock model
        
    Raises:
        ClientError: If there is an error invoking the Bedrock API
        Exception: For other errors during API call or response processing
    """
    try:
        # Call the Bedrock API

        model_id = config.get("Bedrock", "model_id")    
        region = config.get("Bedrock", "region")    
        tuning_args_str = config.get("Bedrock", "tuning_args")
        
        # Create an Amazon Bedrock Runtime client.
        brt = boto3.client("bedrock-runtime", region)
        
        tuning_args = json.loads(tuning_args_str)

        # Format the request payload using the model's native structure.
        native_request = {
            "messages": [           
                    {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"System: {system_prompt}\nUser: {prompt}\n"                    
                        }
                    ]
                }
            ],
        }
        #Add tuning args to native request
        native_request.update(tuning_args)

        # Convert the native request to JSON.
        request = json.dumps(native_request)

        try:
            # Invoke the model with the request.
            response = brt.invoke_model(modelId=model_id, body=request)

        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
            exit(1)

        # Decode the response body.
        model_response = json.loads(response["body"].read())
        #print(model_response)
        # Extract and print the response text.
        response_text = model_response["content"][0]["text"]
        return response_text
    except Exception as e:
        print(f"Error while calling Bedrock: ")
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
        return ""