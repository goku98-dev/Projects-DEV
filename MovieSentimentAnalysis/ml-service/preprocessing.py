# preprocessing.py
import re
import pandas as pd
from sklearn.preprocessing import LabelEncoder

stop_words = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'i', 'me', 'my', 'myself', 'we', 'our',
    'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
    'this', 'these', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'whose', 'why', 'how', 'all', 'any',
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 'can', 'will', 'just', 'don', 'should', 'now'
}

def clean_text(text):
    text = str(text).lower()
    
    text = re.sub(r"<.*?>", "", text)
    
    text = re.sub(r"http\S+|www\S+", "", text)
    
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    
    text = " ".join(word for word in text.split() if word not in stop_words)
    
    return text

def preprocess_dataframe(df, is_labeled=True):
    df = df.copy()
    df['review'] = df['review'].apply(clean_text)
    
    if is_labeled:
        label_encoder = LabelEncoder()
        df['label'] = label_encoder.fit_transform(df['label'])
        return df, label_encoder
    return df