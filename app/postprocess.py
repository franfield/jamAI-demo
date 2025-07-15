import logging
import os
import glob
import json
import tiktoken
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.chat_models import ChatOpenAI

from app.s3_utils import generate_s3_presigned_url

logger = logging.getLogger()
upload_s3_bucket = os.environ.get('UPLOAD_BUCKET_NAME')
resource_s3_bucket = os.environ.get('RESOURCE_BUCKET_NAME')

def process_text(text):
    """
    Process the extracted text from OCR.
    Uses LangChain and OpenAI to process the text with few-shot examples.
    
    Args:
        text (str): The text extracted from OCR
        
    Returns:
        dict: Processing results
    """
    logger.info("Processing extracted text")
    
    try:
        # Read examples from the examples directory
        examples_dir = os.path.join(os.path.dirname(__file__), 'examples')
        examples = []
        for example_file in glob.glob(os.path.join(examples_dir, '*.txt')):
            with open(example_file, 'r') as f:
                content = f.read().strip().split('===')
                examples.append({
                    'input': content[0].strip(),
                    'output': content[1].strip()
                })

        # Read the prompt template from prompt_templates/prompt_template.txt
        template_path = os.path.join(os.path.dirname(__file__), 'prompt_templates', 'prompt_template.txt')
        with open(template_path, 'r') as f:
            template_content = f.read()

        # Create the example template
        example_template = """
        Input: {input}
        Output: {output}
        """

        # Create the few-shot prompt template
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=PromptTemplate(
                input_variables=['input', 'output'],
                template=example_template
            ),
            prefix=template_content,
            suffix="\nInput: {input}\nOutput:",
            input_variables=['input']
        )

        logger.debug("Template content: %s", template_content)
        logger.debug("Example template: %s", example_template)
        logger.debug("Examples: %s", examples)

        # Set up ChatOpenAI
        chat_model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

        prompt_string = few_shot_prompt.format(input=text)
        # Create and invoke the chain
        result = chat_model.predict(prompt_string)
        
        # Debug logging
        logger.debug(f"Raw model response: {result}")
        
        # Clean and parse JSON string into Python dictionary
        try:
            # Clean up the string - remove any leading/trailing whitespace and ensure it's properly formatted
            result = result.strip()
            if result.startswith("```json"):
                # Remove markdown code block markers if present
                result = result.replace("```json", "").replace("```", "").strip()
            
            result_dict = json.loads(result)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {result}")
            logger.error(f"JSON error: {str(e)}")
            result_dict = {"error": "Failed to parse response", "raw_response": result}
        
        # Count tokens in the result
        encoding = tiktoken.encoding_for_model("gpt-4")
        token_count = len(encoding.encode(result)) + len(encoding.encode(prompt_string))
        logger.info(f"Total tokens used: {token_count}")

        # Process the result dictionary
        for key, value in result_dict.items():
            if isinstance(value, dict) and 'chords' in value and value['chords'] is not None:
                chords = value['chords']
                for i in range(len(chords)):
                    chordblock = chords[i]
                    if len(chordblock) == 3:
                        chords[i].append(chords[i][2])
                    if len(chordblock) == 7:
                        chords[i].append(chords[i][6])
            elif isinstance(value, dict) and 'chords' in value and value['chords'] is None:
                logger.error(f"No chords found for {key}")

        for key,value in result_dict.items():
            s3_key_dict = {}
            if isinstance(value, dict) and 'scales' in value and value['scales'] is not None:
                scales = value['scales']
                for scale in scales:
                    #split on space and get first element to determine the key
                    musical_key = scale.split(' ')[0]
                    #take remaining elements and join them with an underscore
                    scale_key = '_'.join(scale.split(' ')[1:]).lower()
                    #add to result_dict
                    s3_key = scale_key + "_" + musical_key + ".txt"
                    url = generate_s3_presigned_url(resource_s3_bucket,s3_key)
                    s3_key_dict[scale] = url
                    #append to result_dict
                    result_dict[key]['urls'] = s3_key_dict
                    

        return result_dict
    
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        return {
            "error": str(e),
            "word_count": len(text.split()),
            "character_count": len(text),
            "processed_text": text  # Return original text in case of error
        } 