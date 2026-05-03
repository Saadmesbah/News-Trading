import re
from difflib import SequenceMatcher

def clean_news_file_regex(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove text after the last " - " on each line
    cleaned = re.sub(r' - [^\n]*', '', content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    print(f"✓ Cleaned file saved to {output_file}")

#clean_news_file_regex('News/NewsText/news_2026-03-30.txt', 'News/NewsText/news_2026-03-30_cleaned.txt')

def clean_news_file_similarity(input_file, output_file, threshold=0.7):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    for line in lines:
        # Remove text after the last " - "
        cleaned_line = re.sub(r' - [^\n]*', '', line).strip()
        
        # Check similarity with already cleaned lines
        if not any(SequenceMatcher(None, cleaned_line, existing).ratio() > threshold for existing in cleaned_lines):
            cleaned_lines.append(cleaned_line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print(f"✓ Cleaned file saved to {output_file}")

clean_news_file_similarity('Cleaning/news_2026-03-30_cleaned.txt', 'Cleaning/news_2026-03-30_final.txt')