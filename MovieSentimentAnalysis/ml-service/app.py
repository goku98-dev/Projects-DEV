from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import joblib
import numpy as np
from preprocessing import clean_text
from rq import Queue
import redis
from datetime import datetime

app = Flask(__name__)
CORS(app) 

#Reddis
try:
    redis_conn = redis.Redis(host='localhost', port=6379)
    redis_conn.ping()
    print("Successfully connected to Redis")
    sentiment_queue = Queue('sentiment_analysis', connection=redis_conn)
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
    redis_conn = None
    sentiment_queue = None

try:
    pipeline = joblib.load('model/sentiment_model.pkl')
    label_encoder = joblib.load('model/label_encoder.pkl')
    print("Model and label encoder loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    pipeline = None
    label_encoder = None

def analyse(review_data):
    try:
        if pipeline is None or label_encoder is None:
            raise Exception("Model not loaded")
        
        review_text = review_data.get('text', '')
        movie_name = review_data.get('movie_name', 'Unknown Movie')
        
        print(f"Sentiment for: {movie_name}")
        
        cleaned_text = clean_text(review_text)
        
        if not cleaned_text.strip():
            raise Exception("Text becomes empty after cleaning")
        
        prediction = pipeline.predict([cleaned_text])[0]
        prediction_proba = pipeline.predict_proba([cleaned_text])[0]
        confidence = float(np.max(prediction_proba))
        sentiment_label = label_encoder.inverse_transform([prediction])[0]
        
        result = {
            "sentiment": sentiment_label,
            "confidence": confidence,
            "movie_name": movie_name,
            "original_text": review_text,
            "cleaned_text": cleaned_text,
            "processed_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        return result
        
    except Exception as e:
        print(f"Error in processing {movie_name}: {str(e)}")
        return {
            "error": str(e),
            "status": "failed",
            "movie_name": movie_name,
            "processed_at": datetime.now().isoformat()
        }

@app.route('/health', methods=['GET'])
def health():
    model_status = "loaded" if pipeline is not None else "not_loaded"
    redis_status = "connected" if redis_conn is not None else "disconnected"
    
    return jsonify({
        "status": "ML service is running",
        "model_status": model_status,
        "redis_status": redis_status,
        "service": "sentiment_analysis"
    })

@app.route('/predict', methods=['POST'])
def sentiment_predict():
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({"error": "Missing text field in request"}), 400
        
        result = analyse(data)
        
        if result.get('status') == 'failed':
            return jsonify(result), 500
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in predict : {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/process-batch', methods=['POST'])
def process_batch():
    try:
        data = request.get_json()
        reviews = data.get('reviews', [])
        
        if not reviews:
            return jsonify({"error": "No reviews provided"}), 400
        
        results = []
        for review_data in reviews:
            result = analyse(review_data)
            results.append(result)
        
        return jsonify({
            "results": results,
            "total_processed": len(results),
            "success": True
        })
        
    except Exception as e:
        print(f"Error in batch processing: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/queue/status', methods=['GET'])
def queue_status():
    try:
        if not sentiment_queue:
            return jsonify({"error": "Queue not available"}), 503
            
        return jsonify({
            "queue_length": len(sentiment_queue),
            "redis_connected": redis_conn is not None,
            "model_loaded": pipeline is not None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/model-info', methods=['GET'])
def model_info():
    if pipeline is None or label_encoder is None:
        return jsonify({
            "model_loaded": False,
            "message": "Model not loaded"
        })
    
    try:
        classes = label_encoder.classes_.tolist()
        return jsonify({
            "model_loaded": True,
            "model_type": "Logistic Regression with TF-IDF",
            "available_classes": classes,
            "message": "Model ready for predictions"
        })
    except Exception as e:
        return jsonify({"error": f"Error getting model info: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting ML Service")
    print("Pipeline loaded ")
    print("Label encoder")
    print("Redis connection")
    
    print("\nAvailable endpoints:")
    print("  - http://localhost:8000/health")
    print("  - http://localhost:8000/predict")
    print("  - http://localhost:8000/process-batch")
    print("  - http://localhost:8000/queue/status")
    print("  - http://localhost:8000/model-info")
    
    app.run(debug=True, port=8000, host='0.0.0.0')