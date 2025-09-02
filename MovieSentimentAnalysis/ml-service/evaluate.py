# evaluate.py
import pandas as pd
import joblib
from sklearn.metrics import classification_report
from preprocessing import preprocess_dataframe

# Load and preprocess labeled data
df = pd.read_csv('data/labeled_data.csv')
df, label_encoder = preprocess_dataframe(df, is_labeled=True)

X = df['review']
y_true = df['label']

# Load model
pipeline = joblib.load('model/sentiment_model.pkl')

# Predict
y_pred = pipeline.predict(X)

# Report
print(classification_report(y_true, y_pred, target_names=label_encoder.classes_))
