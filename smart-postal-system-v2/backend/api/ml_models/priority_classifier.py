import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os

class PriorityClassifier:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.scaler = None
        self.feature_names = []
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        model_path = os.path.join(os.path.dirname(__file__), 'model1_priority_classifier.pkl')
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['model']
                self.encoders = model_data['encoders']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    
    def preprocess_features(self, mail_data: dict) -> np.ndarray:
        """Preprocess single mail item for prediction"""
        df = pd.DataFrame([mail_data])
        
        # Encode categorical features
        categorical_features = ['mail_type', 'sender_type', 'recipient_type', 
                               'time_received', 'day_of_week']
        
        for feature in categorical_features:
            df[f'{feature}_encoded'] = self.encoders[feature].transform(df[feature])
        
        # Temporal features
        time_to_category = {
            '08:00': 0, '09:30': 0,
            '11:00': 1, '13:00': 1,
            '14:30': 2, '16:00': 2
        }
        df['time_category'] = df['time_received'].map(time_to_category)
        
        # Binary indicators
        df['is_priority_sender'] = df['sender_type'].isin(
            ['court', 'law_firm', 'government_office', 'tax_office']
        ).astype(int)
        
        df['is_priority_mail'] = df['mail_type'].isin(
            ['court_notice', 'legal_document', 'registered_letter', 
             'speed_post', 'express_mail', 'tax_document', 'certificate']
        ).astype(int)
        
        df['is_early_week'] = df['day_of_week'].isin(['monday', 'tuesday']).astype(int)
        df['is_morning'] = df['time_received'].isin(['08:00', '09:30']).astype(int)
        
        # Interaction features
        df['priority_sender_mail'] = df['is_priority_sender'] * df['is_priority_mail']
        df['morning_priority'] = df['is_morning'] * df['is_priority_mail']
        df['early_week_priority'] = df['is_early_week'] * df['is_priority_mail']
        df['morning_early_week'] = df['is_morning'] * df['is_early_week']
        
        # Select features
        X = df[self.feature_names].values
        
        # Scale
        X = self.scaler.transform(X)
        
        return X
    
    def predict(self, mail_data: dict) -> dict:
        """Predict priority for mail item"""
        try:
            X = self.preprocess_features(mail_data)
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            priority_label = self.encoders['target'].inverse_transform([prediction])[0]
            
            return {
                'priority': priority_label,
                'confidence': float(probabilities.max()),
                'probability_regular': float(probabilities[0]),
                'probability_urgent': float(probabilities[1]),
            }
        except Exception as e:
            return {'error': str(e)}