import tiktoken

def calculate_tokens(text: str, model_encoding: str = "cl100k_base"):
    """
    Calculates the number of tokens in a string.
    Default encoding 'cl100k_base' is used by GPT-4 and many Llama-based APIs.
    """
    # Load the encoding
    encoding = tiktoken.get_encoding(model_encoding)
    
    # Encode the text into integers
    tokens = encoding.encode(text)
    
    # Calculate counts
    num_tokens = len(tokens)
    
    return num_tokens, tokens

# Example usage
with open('Cleaning/news_2026-03-30.txt', 'r', encoding='utf-8') as f:
    Input_text = f.read()
count, token_list = calculate_tokens(Input_text)

print(f"Token Count: {count}")
