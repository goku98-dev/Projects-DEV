# train_model.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib
from preprocessing import preprocess_dataframe

# Load data
df = pd.read_csv('data/reviews_labeled.csv')

# Preprocess
df, label_encoder = preprocess_dataframe(df, is_labeled=True)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    df['review'], df['label'], test_size=0.2, stratify=df['label'], random_state=42
)

# Build pipeline
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ('clf', LogisticRegression(max_iter=1000))
])

# Train
pipeline.fit(X_train, y_train)

# Evaluate
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model and label encoder
joblib.dump(pipeline, 'model/sentiment_model.pkl')
joblib.dump(label_encoder, 'model/label_encoder.pkl')
