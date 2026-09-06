import os
import argparse
import pandas as pd
import numpy as np
import hashlib
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure NLTK data is downloaded
for _pkg, _name in [
    ('corpora/stopwords', 'stopwords'),
    ('tokenizers/punkt', 'punkt'),
    ('tokenizers/punkt_tab', 'punkt_tab'),
    ('corpora/wordnet', 'wordnet'),
]:
    try:
        nltk.data.find(_pkg)
    except LookupError:
        nltk.download(_name, quiet=True)

def clean_data(input_dir, output_dir):
    # Create output dir
    os.makedirs(output_dir, exist_ok=True)
    
    bugs_path = os.path.join(input_dir, 'bugs_raw.csv')
    logs_path = os.path.join(input_dir, 'logs_raw.csv')
    screenshots_path = os.path.join(input_dir, 'screenshots_raw.csv')
    resolutions_path = os.path.join(input_dir, 'resolutions_raw.csv')
    
    bugs_df = pd.read_csv(bugs_path) if os.path.exists(bugs_path) else pd.DataFrame(columns=['bug_id', 'title', 'description', 'module', 'environment'])
    logs_df = pd.read_csv(logs_path) if os.path.exists(logs_path) else pd.DataFrame(columns=['bug_id', 'log_content'])
    screenshots_df = pd.read_csv(screenshots_path) if os.path.exists(screenshots_path) else pd.DataFrame(columns=['bug_id', 'ui_page', 'user_action', 'visible_fields'])
    resolutions_df = pd.read_csv(resolutions_path) if os.path.exists(resolutions_path) else pd.DataFrame(columns=['bug_id', 'reproducible_steps', 'root_cause'])

    print("=== BEFORE CLEANING ===")
    print(f"Total records: {len(bugs_df)}")
    
    missing_desc_before = bugs_df['description'].isna().sum() if not bugs_df.empty else 0
    print(f"Missing descriptions: {missing_desc_before} ({(missing_desc_before/len(bugs_df)*100 if len(bugs_df) > 0 else 0):.2f}%)")

    # 1. Missing Data Handling
    if not bugs_df.empty:
        bugs_df['description'] = bugs_df['description'].fillna('NO_DESCRIPTION_PROVIDED')
        if 'environment' not in bugs_df.columns:
            bugs_df['environment'] = 'UNSPECIFIED'
        else:
            bugs_df['environment'] = bugs_df['environment'].fillna('UNSPECIFIED')

    if not logs_df.empty:
        logs_df['log_content'] = logs_df['log_content'].fillna('NO_LOG_AVAILABLE')

    if not screenshots_df.empty:
        for col in ['ui_page', 'user_action', 'visible_fields']:
            if col in screenshots_df.columns:
                screenshots_df[col] = screenshots_df[col].fillna('UNKNOWN')

    # 2. Duplicate Detection
    def get_hash(row):
        s = f"{row.get('title', '')}{row.get('description', '')}{row.get('module', '')}"
        return hashlib.md5(s.encode('utf-8')).hexdigest()
    
    exact_dupes_removed = 0
    if not bugs_df.empty:
        bugs_df['hash'] = bugs_df.apply(get_hash, axis=1)
        initial_count = len(bugs_df)
        bugs_df = bugs_df.drop_duplicates(subset=['hash'])
        exact_dupes_removed = initial_count - len(bugs_df)
        bugs_df = bugs_df.drop(columns=['hash'])

    semantic_dupes_count = 0
    if not bugs_df.empty:
        bugs_df['is_semantic_duplicate'] = False
        if len(bugs_df) > 1:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(bugs_df['description'])
            cosine_sim = cosine_similarity(tfidf_matrix)
            
            indices = np.where(cosine_sim > 0.92)
            duplicates_to_flag = set()
            for i, j in zip(*indices):
                if i != j and j not in duplicates_to_flag and i not in duplicates_to_flag:
                    duplicates_to_flag.add(j)
            
            for idx in duplicates_to_flag:
                bugs_df.iloc[idx, bugs_df.columns.get_loc('is_semantic_duplicate')] = True
            semantic_dupes_count = len(duplicates_to_flag)

    # 3. Log Cleaning
    def clean_log(log_text):
        if not isinstance(log_text, str) or log_text == 'NO_LOG_AVAILABLE':
            return log_text
        log_text = re.sub(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}', '', log_text)
        
        lines = log_text.split('\n')
        cleaned_lines = []
        keywords = ['error', 'exception', 'fail', 'warn', 'timeout', 'deadlock', 'rollback', 'null', 'invalid']
        keep_levels = ['ERROR', 'WARN', 'EXCEPTION', 'FATAL']
        
        for line in lines:
            line_lower = line.lower()
            if any(level in line for level in keep_levels):
                cleaned_lines.append(line)
            elif 'info' in line_lower:
                if any(kw in line_lower for kw in keywords):
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    if not logs_df.empty:
        logs_df['log_content_clean'] = logs_df['log_content'].apply(clean_log)

    # 4. Text NLP Cleaning
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    def nlp_clean(text):
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-z\s]', '', text)
        tokens = word_tokenize(text)
        cleaned_tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
        return ' '.join(cleaned_tokens)

    if not bugs_df.empty:
        bugs_df['title_clean'] = bugs_df.get('title', pd.Series(dtype=str)).apply(nlp_clean)
        bugs_df['description_clean'] = bugs_df['description'].apply(nlp_clean)

    # 5. Screenshot Metadata Normalization
    def norm_page(text):
        if not isinstance(text, str) or text == 'UNKNOWN': return text
        text = text.strip().title()
        if text.lower() == 'inv approval':
            return 'Invoice Approval Screen'
        return text

    def norm_action(text):
        if not isinstance(text, str) or text == 'UNKNOWN': return text
        return text.strip().lower()

    def norm_fields(text):
        if not isinstance(text, str) or text == 'UNKNOWN': return text
        fields = [f.strip() for f in text.split(',')]
        return ','.join(sorted(list(set(fields))))

    if not screenshots_df.empty:
        if 'ui_page' in screenshots_df.columns:
            screenshots_df['ui_page'] = screenshots_df['ui_page'].apply(norm_page)
        if 'user_action' in screenshots_df.columns:
            screenshots_df['user_action'] = screenshots_df['user_action'].apply(norm_action)
        if 'visible_fields' in screenshots_df.columns:
            screenshots_df['visible_fields'] = screenshots_df['visible_fields'].apply(norm_fields)

    # 6. Output
    bugs_df.to_csv(os.path.join(output_dir, 'bugs_cleaned.csv'), index=False)
    logs_df.to_csv(os.path.join(output_dir, 'logs_cleaned.csv'), index=False)
    screenshots_df.to_csv(os.path.join(output_dir, 'screenshots_cleaned.csv'), index=False)
    resolutions_df.to_csv(os.path.join(output_dir, 'resolutions_cleaned.csv'), index=False)

    print("\n=== AFTER CLEANING ===")
    missing_desc_after = bugs_df['description'].isna().sum() if not bugs_df.empty else 0
    print(f"Missing descriptions: {missing_desc_after} ({(missing_desc_after/len(bugs_df)*100 if len(bugs_df) > 0 else 0):.2f}%)")
    print(f"Exact duplicates removed: {exact_dupes_removed}")
    print(f"Semantic duplicates flagged: {semantic_dupes_count}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Data Cleaning Pipeline")
    parser.add_argument('--input-dir', default='data/raw', help="Input directory")
    parser.add_argument('--output-dir', default='data/cleaned', help="Output directory")
    args = parser.parse_args()
    clean_data(args.input_dir, args.output_dir)
