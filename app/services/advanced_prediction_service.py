# app/services/advanced_prediction_service.py
# Advanced prediction service with Prophet, ARIMA, and time series validation

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from pathlib import Path
from datetime import datetime, timedelta
import warnings
import json
from typing import Dict, List, Tuple, Optional

# Standard ML imports
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.preprocessing import StandardScaler

# Time series specific imports
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except (ImportError, Exception) as e:
    PROPHET_AVAILABLE = False
    logger.info(f"⚠️ Prophet not available: {e} - fallback to other models")
    Prophet = None

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.stats.diagnostic import acorr_ljungbox
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("⚠️ Statsmodels not available - install with: pip install statsmodels")

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class AdvancedPredictionService:
    """
    Advanced prediction service with specialized time series models
    """
    
    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.models = {}
        self.model_metrics = {}
        self.predictions = {}
        self.cv_results = {}
        
        # Output folder for results
        self.output_folder = Path("app/static/img/predictions")
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Model configurations
        self.model_configs = {
            'prophet': {'enabled': PROPHET_AVAILABLE},
            'arima': {'enabled': STATSMODELS_AVAILABLE},
            'random_forest': {'enabled': True},
            'linear_regression': {'enabled': True}
        }
    
    def time_series_split_validation(self, X, y, dates, n_splits=5):
        """
        Perform time series cross-validation
        """
        logger.info(f"=== VALIDATION CROISÉE TEMPORELLE ({n_splits} splits) ===")
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        cv_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Train a simple model for validation
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            cv_scores.append({'fold': fold, 'r2': r2, 'mae': mae})
            
            logger.info(f"Fold {fold+1}: R²={r2:.3f}, MAE={mae:.2f}")
        
        cv_results = {
            'mean_r2': np.mean([s['r2'] for s in cv_scores]),
            'std_r2': np.std([s['r2'] for s in cv_scores]),
            'mean_mae': np.mean([s['mae'] for s in cv_scores]),
            'scores': cv_scores
        }
        
        logger.info(f"✅ CV Results: R²={cv_results['mean_r2']:.3f}±{cv_results['std_r2']:.3f}")
        
        self.cv_results = cv_results
        return cv_results
    
    def train_prophet_model(self, data):
        """
        Train Facebook Prophet model
        """
        if not PROPHET_AVAILABLE or Prophet is None:
            logger.warning("⚠️ Prophet not available - skipping Prophet model")
            return None
        
        logger.info("=== ENTRAÎNEMENT PROPHET ===")
        
        try:
            # Prepare data for Prophet (requires 'ds' and 'y' columns)
            prophet_data = pd.DataFrame({
                'ds': data['dates'],
                'y': data['y']
            })
            
            # Initialize Prophet with parameters
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,
                seasonality_mode='multiplicative'
            )
            
            # Add custom seasonalities
            model.add_seasonality(name='quarterly', period=91.25, fourier_order=4)
            
            # Fit the model
            model.fit(prophet_data)
            
            # Make predictions on training data for evaluation
            forecast = model.predict(prophet_data)
            
            # Calculate metrics
            y_true = prophet_data['y'].values
            y_pred = forecast['yhat'].values
            
            r2 = r2_score(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            
            metrics = {
                'r2_score': r2,
                'mae': mae,
                'rmse': rmse,
                'model_type': 'prophet'
            }
            
            logger.info(f"✅ Prophet trained - R²: {r2:.3f}, MAE: {mae:.2f}")
            
            return {
                'model': model,
                'metrics': metrics,
                'forecast': forecast
            }
            
        except Exception as e:
            logger.error(f"❌ Error training Prophet: {e}")
            return None
    
    def train_arima_model(self, data, order=(2,1,2)):
        """
        Train ARIMA model
        """
        if not STATSMODELS_AVAILABLE:
            logger.warning("⚠️ Statsmodels not available")
            return None
        
        logger.info(f"=== ENTRAÎNEMENT ARIMA{order} ===")
        
        try:
            # Prepare time series data
            ts_data = pd.Series(data['y'].values, index=data['dates'])
            ts_data = ts_data.asfreq('MS')  # Monthly start frequency
            
            # Handle missing values
            ts_data = ts_data.ffill()
            
            # Fit ARIMA model
            model = ARIMA(ts_data, order=order)
            fitted_model = model.fit()
            
            # Make predictions
            y_pred = fitted_model.fittedvalues
            y_true = ts_data.values
            
            # Calculate metrics
            r2 = r2_score(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            
            # Model diagnostics
            ljung_box = acorr_ljungbox(fitted_model.resid, lags=10, return_df=True)
            aic = fitted_model.aic
            bic = fitted_model.bic
            
            metrics = {
                'r2_score': r2,
                'mae': mae,
                'rmse': rmse,
                'aic': aic,
                'bic': bic,
                'ljung_box_pvalue': ljung_box['lb_pvalue'].iloc[0],
                'model_type': 'arima',
                'order': order
            }
            
            logger.info(f"✅ ARIMA trained - R²: {r2:.3f}, MAE: {mae:.2f}, AIC: {aic:.1f}")
            
            return {
                'model': fitted_model,
                'metrics': metrics,
                'residuals': fitted_model.resid
            }
            
        except Exception as e:
            logger.error(f"❌ Error training ARIMA: {e}")
            return None
    
    def hyperparameter_tuning_rf(self, X, y):
        """
        Simple hyperparameter tuning for Random Forest
        """
        logger.info("=== HYPERPARAMETER TUNING RANDOM FOREST ===")
        
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, None],
            'min_samples_split': [2, 5, 10]
        }
        
        best_score = -np.inf
        best_params = None
        best_model = None
        
        # Simple grid search with time series split
        tscv = TimeSeriesSplit(n_splits=3)
        
        for n_est in param_grid['n_estimators']:
            for max_d in param_grid['max_depth']:
                for min_split in param_grid['min_samples_split']:
                    
                    scores = []
                    for train_idx, test_idx in tscv.split(X):
                        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                        
                        model = RandomForestRegressor(
                            n_estimators=n_est,
                            max_depth=max_d,
                            min_samples_split=min_split,
                            random_state=42
                        )
                        model.fit(X_train, y_train)
                        y_pred = model.predict(X_test)
                        scores.append(r2_score(y_test, y_pred))
                    
                    avg_score = np.mean(scores)
                    
                    if avg_score > best_score:
                        best_score = avg_score
                        best_params = {
                            'n_estimators': n_est,
                            'max_depth': max_d,
                            'min_samples_split': min_split
                        }
        
        # Train final model with best parameters
        best_model = RandomForestRegressor(**best_params, random_state=42)
        best_model.fit(X, y)
        
        logger.info(f"✅ Best RF params: {best_params}, Score: {best_score:.3f}")
        
        return best_model, best_params, best_score
    
    def train_all_advanced_models(self):
        """
        Train all available models with advanced features
        """
        logger.info("=== ENTRAÎNEMENT MODÈLES AVANCÉS ===")
        
        # Get prepared data
        ml_data = self.preprocessor.prepare_ml_datasets()
        
        if len(ml_data['X']) < 10:
            logger.error("❌ Not enough data for training")
            return None
        
        # Perform time series cross-validation
        self.time_series_split_validation(ml_data['X'], ml_data['y'], ml_data['dates'])
        
        results = {}
        
        # 1. Prophet model
        if self.model_configs['prophet']['enabled']:
            prophet_result = self.train_prophet_model(ml_data)
            if prophet_result:
                results['prophet'] = prophet_result
        
        # 2. ARIMA model
        if self.model_configs['arima']['enabled']:
            arima_result = self.train_arima_model(ml_data)
            if arima_result:
                results['arima'] = arima_result
        
        # 3. Enhanced Random Forest with hyperparameter tuning
        try:
            rf_model, rf_params, rf_score = self.hyperparameter_tuning_rf(ml_data['X'], ml_data['y'])
            y_pred = rf_model.predict(ml_data['X'])
            
            results['random_forest_tuned'] = {
                'model': rf_model,
                'metrics': {
                    'r2_score': r2_score(ml_data['y'], y_pred),
                    'mae': mean_absolute_error(ml_data['y'], y_pred),
                    'rmse': np.sqrt(mean_squared_error(ml_data['y'], y_pred)),
                    'model_type': 'random_forest_tuned',
                    'best_params': rf_params
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error training tuned RF: {e}")
        
        # 4. Linear regression with feature scaling
        try:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(ml_data['X'])
            
            lr_model = LinearRegression()
            lr_model.fit(X_scaled, ml_data['y'])
            y_pred = lr_model.predict(X_scaled)
            
            results['linear_regression_scaled'] = {
                'model': lr_model,
                'scaler': scaler,
                'metrics': {
                    'r2_score': r2_score(ml_data['y'], y_pred),
                    'mae': mean_absolute_error(ml_data['y'], y_pred),
                    'rmse': np.sqrt(mean_squared_error(ml_data['y'], y_pred)),
                    'model_type': 'linear_regression_scaled'
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error training scaled LR: {e}")
        
        # Store results
        self.models = results
        self.model_metrics = {k: v['metrics'] for k, v in results.items() if 'metrics' in v}
        
        # Find best model
        best_model_name = max(self.model_metrics.keys(), 
                             key=lambda k: self.model_metrics[k]['r2_score'])
        
        logger.info(f"🏆 Best model: {best_model_name} (R²={self.model_metrics[best_model_name]['r2_score']:.3f})")
        
        return results
    
    def generate_future_predictions(self, periods=24):
        """
        Generate future predictions using the best available model
        """
        logger.info(f"=== PRÉDICTIONS FUTURES ({periods} périodes) ===")
        
        if not self.models:
            logger.error("❌ No trained models available")
            return None
        
        predictions = {}
        
        # Get best model
        best_model_name = max(self.model_metrics.keys(), 
                             key=lambda k: self.model_metrics[k]['r2_score'])
        
        logger.info(f"Using best model: {best_model_name}")
        
        # Generate predictions based on model type
        if best_model_name == 'prophet' and 'prophet' in self.models:
            predictions = self._predict_with_prophet(periods)
        elif best_model_name == 'arima' and 'arima' in self.models:
            predictions = self._predict_with_arima(periods)
        else:
            predictions = self._predict_with_ml_model(best_model_name, periods)
        
        self.predictions = predictions
        return predictions
    
    def _predict_with_prophet(self, periods):
        """Predict with Prophet model"""
        model = self.models['prophet']['model']
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq='MS')
        forecast = model.predict(future)
        
        # Extract future predictions
        future_start = len(forecast) - periods
        future_predictions = forecast.iloc[future_start:]['yhat'].values
        future_dates = forecast.iloc[future_start:]['ds'].values
        
        return {
            'model_name': 'prophet',
            'predictions': future_predictions.tolist(),
            'dates': [pd.to_datetime(d).strftime('%Y-%m') for d in future_dates],
            'confidence_intervals': {
                'lower': forecast.iloc[future_start:]['yhat_lower'].values.tolist(),
                'upper': forecast.iloc[future_start:]['yhat_upper'].values.tolist()
            }
        }
    
    def _predict_with_arima(self, periods):
        """Predict with ARIMA model"""
        model = self.models['arima']['model']
        
        # Generate future predictions
        forecast = model.forecast(steps=periods)
        conf_int = model.get_forecast(steps=periods).conf_int()
        
        # Generate future dates
        last_date = self.preprocessor.df_features['date'].max()
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                   periods=periods, freq='MS')
        
        return {
            'model_name': 'arima',
            'predictions': forecast.tolist(),
            'dates': [d.strftime('%Y-%m') for d in future_dates],
            'confidence_intervals': {
                'lower': conf_int.iloc[:, 0].tolist(),
                'upper': conf_int.iloc[:, 1].tolist()
            }
        }
    
    def _predict_with_ml_model(self, model_name, periods):
        """Predict with ML models using trend extrapolation"""
        # Simple trend-based prediction for ML models
        ml_data = self.preprocessor.prepare_ml_datasets()
        last_values = ml_data['y'].tail(12).values  # Last 12 months
        
        # Simple trend calculation
        trend = np.polyfit(range(len(last_values)), last_values, 1)[0]
        
        # Generate future predictions
        future_predictions = []
        last_value = last_values[-1]
        
        for i in range(periods):
            next_pred = last_value + trend * (i + 1)
            # Add some seasonal variation
            seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * i / 12)
            next_pred *= seasonal_factor
            future_predictions.append(max(1, next_pred))  # Ensure positive
        
        # Generate future dates
        last_date = ml_data['dates'].max()
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), 
                                   periods=periods, freq='MS')
        
        return {
            'model_name': model_name,
            'predictions': future_predictions,
            'dates': [d.strftime('%Y-%m') for d in future_dates],
            'confidence_intervals': {
                'lower': [p * 0.8 for p in future_predictions],
                'upper': [p * 1.2 for p in future_predictions]
            }
        }
    
    def get_model_comparison(self):
        """
        Get comprehensive model comparison
        """
        if not self.model_metrics:
            return {}
        
        comparison = {}
        for model_name, metrics in self.model_metrics.items():
            r2 = metrics['r2_score']
            
            # Determine quality rating
            if r2 > 0.8:
                quality = 'Excellent'
            elif r2 > 0.5:
                quality = 'Bon'
            elif r2 > 0.2:
                quality = 'Moyen'
            else:
                quality = 'Faible'
            
            comparison[model_name] = {
                'r2_score': r2,
                'mae': metrics['mae'],
                'quality': quality,
                'model_type': metrics['model_type']
            }
        
        return comparison
    
    def export_results(self):
        """
        Export all results to JSON for web interface
        """
        results = {
            'model_comparison': self.get_model_comparison(),
            'cv_results': self.cv_results,
            'predictions': self.predictions,
            'preprocessing_summary': self.preprocessor.get_preprocessing_summary(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to file
        results_path = self.output_folder / 'advanced_results.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"✅ Results exported to {results_path}")
        
        return results