# predict.py
import pandas as pd
import joblib
from preprocessing import preprocess_dataframe

# Load model and data
pipeline = joblib.load('model/sentiment_model.pkl')
label_encoder = joblib.load('model/label_encoder.pkl')
df_unlabeled = pd.read_csv('data/reviews_unlabeled.csv')

# Preprocess
df_unlabeled = preprocess_dataframe(df_unlabeled, is_labeled=False)

# Predict
predictions = pipeline.predict(df_unlabeled['review'])
df_unlabeled['predicted_label'] = label_encoder.inverse_transform(predictions)

# Save results
df_unlabeled.to_csv('data/unlabeled_with_predictions.csv', index=False)
print(df_unlabeled[['review', 'predicted_label']].head())
