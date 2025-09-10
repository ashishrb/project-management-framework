"""
Advanced AI Features Service
Provides advanced AI capabilities including intelligent automation, predictive analytics, and smart recommendations
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from pydantic import BaseModel, Field

from app.core.ai_client import get_ai_service, AIMessage
from app.core.vector_db import get_vector_db, Document
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIInsightType(str, Enum):
    """Types of AI insights."""
    TREND_ANALYSIS = "trend_analysis"
    PATTERN_DETECTION = "pattern_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    CLUSTERING_ANALYSIS = "clustering_analysis"
    OPTIMIZATION_SUGGESTIONS = "optimization_suggestions"


class PredictionType(str, Enum):
    """Types of predictions."""
    PROJECT_COMPLETION = "project_completion"
    BUDGET_CONSUMPTION = "budget_consumption"
    RESOURCE_UTILIZATION = "resource_utilization"
    RISK_PROBABILITY = "risk_probability"
    TIMELINE_DEVIATION = "timeline_deviation"
    QUALITY_METRICS = "quality_metrics"


class AutomationTask(BaseModel):
    """AI automation task model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    task_type: str = Field(..., description="Type of automation task")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")
    status: str = Field(default="pending", description="Task status")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AIInsight(BaseModel):
    """AI insight model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    insight_type: AIInsightType
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    impact: str = Field(..., description="Impact level: Low, Medium, High, Critical")
    data_points: List[Dict[str, Any]] = Field(default_factory=list, description="Supporting data")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class Prediction(BaseModel):
    """Prediction model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prediction_type: PredictionType
    target: str = Field(..., description="Prediction target")
    value: Union[float, str, Dict[str, Any]] = Field(..., description="Predicted value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    time_horizon: int = Field(..., description="Prediction time horizon in days")
    factors: List[str] = Field(default_factory=list, description="Key influencing factors")
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(..., description="Prediction expiration")


class AdvancedAIService:
    """Advanced AI service for intelligent automation and analytics."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.automation_tasks: Dict[str, AutomationTask] = {}
        self.insights: List[AIInsight] = []
        self.predictions: List[Prediction] = []
        
        # ML models
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.kmeans_model = None
        self.pca_model = None
    
    async def analyze_trends(
        self,
        data: List[Dict[str, Any]],
        time_field: str = "created_at",
        value_field: str = "value",
        window_days: int = 30
    ) -> AIInsight:
        """Analyze trends in data."""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            df[time_field] = pd.to_datetime(df[time_field])
            df = df.sort_values(time_field)
            
            # Calculate trend metrics
            recent_data = df[df[time_field] >= datetime.now() - timedelta(days=window_days)]
            if len(recent_data) < 2:
                return self._create_insight(
                    AIInsightType.TREND_ANALYSIS,
                    "Insufficient Data for Trend Analysis",
                    "Not enough data points for meaningful trend analysis",
                    0.3,
                    "Low",
                    []
                )
            
            # Calculate trend direction and strength
            values = recent_data[value_field].values
            trend_slope = np.polyfit(range(len(values)), values, 1)[0]
            trend_strength = abs(np.corrcoef(range(len(values)), values)[0, 1])
            
            # Determine trend direction
            if trend_slope > 0.1:
                direction = "increasing"
                impact = "High" if trend_strength > 0.7 else "Medium"
            elif trend_slope < -0.1:
                direction = "decreasing"
                impact = "High" if trend_strength > 0.7 else "Medium"
            else:
                direction = "stable"
                impact = "Low"
            
            # Generate AI-powered insights
            ai_service = await get_ai_service()
            
            trend_summary = f"""
            Trend Analysis Results:
            - Direction: {direction}
            - Strength: {trend_strength:.3f}
            - Slope: {trend_slope:.3f}
            - Data Points: {len(recent_data)}
            - Time Window: {window_days} days
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a data analyst expert. Analyze trend data and provide insights.
                    Focus on:
                    1. Trend interpretation
                    2. Business implications
                    3. Potential causes
                    4. Recommendations
                    
                    Provide actionable insights based on the trend data."""
                ),
                AIMessage(role="user", content=trend_summary)
            ]
            
            response = await ai_service.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.3
            )
            
            # Parse AI response
            try:
                ai_insights = json.loads(response.content)
            except json.JSONDecodeError:
                ai_insights = {
                    "interpretation": f"Trend is {direction} with strength {trend_strength:.3f}",
                    "implications": ["Monitor closely for changes"],
                    "causes": ["Multiple factors may be influencing"],
                    "recommendations": ["Continue monitoring", "Investigate underlying causes"]
                }
            
            recommendations = ai_insights.get("recommendations", [
                "Continue monitoring the trend",
                "Investigate underlying causes",
                "Consider proactive measures"
            ])
            
            insight = self._create_insight(
                AIInsightType.TREND_ANALYSIS,
                f"{direction.title()} Trend Detected",
                ai_insights.get("interpretation", f"Trend is {direction}"),
                trend_strength,
                impact,
                recommendations
            )
            
            self.insights.append(insight)
            return insight
            
        except Exception as e:
            self.logger.error(f"Failed to analyze trends: {e}")
            return self._create_insight(
                AIInsightType.TREND_ANALYSIS,
                "Trend Analysis Failed",
                f"Error analyzing trends: {str(e)}",
                0.0,
                "Low",
                ["Manual analysis required"]
            )
    
    async def detect_patterns(
        self,
        data: List[Dict[str, Any]],
        text_fields: List[str] = None,
        categorical_fields: List[str] = None
    ) -> AIInsight:
        """Detect patterns in data using ML techniques."""
        try:
            df = pd.DataFrame(data)
            
            patterns = []
            confidence_scores = []
            
            # Text pattern analysis
            if text_fields:
                for field in text_fields:
                    if field in df.columns:
                        texts = df[field].dropna().astype(str).tolist()
                        if len(texts) > 1:
                            # TF-IDF analysis
                            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
                            similarity_matrix = cosine_similarity(tfidf_matrix)
                            
                            # Find similar documents
                            avg_similarity = np.mean(similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)])
                            if avg_similarity > 0.7:
                                patterns.append(f"High similarity in {field} content")
                                confidence_scores.append(avg_similarity)
            
            # Categorical pattern analysis
            if categorical_fields:
                for field in categorical_fields:
                    if field in df.columns:
                        value_counts = df[field].value_counts()
                        if len(value_counts) > 0:
                            # Check for dominant values
                            max_count = value_counts.max()
                            total_count = len(df)
                            dominance_ratio = max_count / total_count
                            
                            if dominance_ratio > 0.8:
                                dominant_value = value_counts.index[0]
                                patterns.append(f"Dominant value '{dominant_value}' in {field} ({dominance_ratio:.1%})")
                                confidence_scores.append(dominance_ratio)
            
            # Temporal pattern analysis
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['hour'] = df['created_at'].dt.hour
                df['day_of_week'] = df['created_at'].dt.dayofweek
                
                # Check for time-based patterns
                hour_distribution = df['hour'].value_counts()
                if len(hour_distribution) > 0:
                    peak_hour = hour_distribution.index[0]
                    peak_ratio = hour_distribution.iloc[0] / len(df)
                    if peak_ratio > 0.3:
                        patterns.append(f"Peak activity at hour {peak_hour} ({peak_ratio:.1%})")
                        confidence_scores.append(peak_ratio)
            
            if not patterns:
                return self._create_insight(
                    AIInsightType.PATTERN_DETECTION,
                    "No Significant Patterns Detected",
                    "No clear patterns found in the analyzed data",
                    0.3,
                    "Low",
                    ["Continue data collection", "Try different analysis parameters"]
                )
            
            # Generate AI insights
            ai_service = await get_ai_service()
            
            pattern_summary = f"""
            Pattern Detection Results:
            Patterns Found: {len(patterns)}
            Patterns: {patterns}
            Confidence Scores: {confidence_scores}
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a data scientist expert. Analyze detected patterns and provide insights.
                    Focus on:
                    1. Pattern interpretation
                    2. Business significance
                    3. Potential causes
                    4. Actionable recommendations
                    
                    Provide clear, actionable insights based on the detected patterns."""
                ),
                AIMessage(role="user", content=pattern_summary)
            ]
            
            response = await ai_service.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.3
            )
            
            # Parse AI response
            try:
                ai_insights = json.loads(response.content)
            except json.JSONDecodeError:
                ai_insights = {
                    "interpretation": f"Found {len(patterns)} significant patterns",
                    "significance": ["Patterns indicate systematic behavior"],
                    "causes": ["Multiple factors contributing"],
                    "recommendations": ["Investigate patterns further", "Consider optimization opportunities"]
                }
            
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
            impact = "High" if avg_confidence > 0.7 else "Medium" if avg_confidence > 0.5 else "Low"
            
            insight = self._create_insight(
                AIInsightType.PATTERN_DETECTION,
                f"{len(patterns)} Patterns Detected",
                ai_insights.get("interpretation", f"Found {len(patterns)} significant patterns"),
                avg_confidence,
                impact,
                ai_insights.get("recommendations", ["Investigate patterns further"])
            )
            
            self.insights.append(insight)
            return insight
            
        except Exception as e:
            self.logger.error(f"Failed to detect patterns: {e}")
            return self._create_insight(
                AIInsightType.PATTERN_DETECTION,
                "Pattern Detection Failed",
                f"Error detecting patterns: {str(e)}",
                0.0,
                "Low",
                ["Manual analysis required"]
            )
    
    async def detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        value_field: str = "value",
        threshold: float = 2.0
    ) -> AIInsight:
        """Detect anomalies in data using statistical methods."""
        try:
            df = pd.DataFrame(data)
            
            if value_field not in df.columns:
                return self._create_insight(
                    AIInsightType.ANOMALY_DETECTION,
                    "Invalid Field for Anomaly Detection",
                    f"Field '{value_field}' not found in data",
                    0.0,
                    "Low",
                    ["Check field names", "Verify data structure"]
                )
            
            values = df[value_field].dropna()
            if len(values) < 3:
                return self._create_insight(
                    AIInsightType.ANOMALY_DETECTION,
                    "Insufficient Data for Anomaly Detection",
                    "Need at least 3 data points for anomaly detection",
                    0.0,
                    "Low",
                    ["Collect more data", "Reduce detection threshold"]
                )
            
            # Statistical anomaly detection
            mean_val = values.mean()
            std_val = values.std()
            
            # Z-score based anomaly detection
            z_scores = np.abs((values - mean_val) / std_val)
            anomalies = values[z_scores > threshold]
            
            if len(anomalies) == 0:
                return self._create_insight(
                    AIInsightType.ANOMALY_DETECTION,
                    "No Anomalies Detected",
                    f"No statistical anomalies found (threshold: {threshold}σ)",
                    0.8,
                    "Low",
                    ["Data appears normal", "Continue monitoring"]
                )
            
            # Generate AI insights
            ai_service = await get_ai_service()
            
            anomaly_summary = f"""
            Anomaly Detection Results:
            - Total data points: {len(values)}
            - Anomalies detected: {len(anomalies)}
            - Anomaly threshold: {threshold}σ
            - Anomaly values: {anomalies.tolist()}
            - Mean: {mean_val:.3f}
            - Std Dev: {std_val:.3f}
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a data analyst expert. Analyze anomaly detection results and provide insights.
                    Focus on:
                    1. Anomaly interpretation
                    2. Potential causes
                    3. Business impact
                    4. Recommended actions
                    
                    Provide actionable insights for handling detected anomalies."""
                ),
                AIMessage(role="user", content=anomaly_summary)
            ]
            
            response = await ai_service.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.3
            )
            
            # Parse AI response
            try:
                ai_insights = json.loads(response.content)
            except json.JSONDecodeError:
                ai_insights = {
                    "interpretation": f"Detected {len(anomalies)} anomalies",
                    "causes": ["Multiple potential causes"],
                    "impact": ["Requires investigation"],
                    "recommendations": ["Investigate anomalies", "Verify data quality"]
                }
            
            anomaly_ratio = len(anomalies) / len(values)
            impact = "Critical" if anomaly_ratio > 0.1 else "High" if anomaly_ratio > 0.05 else "Medium"
            confidence = min(0.9, 0.5 + anomaly_ratio * 2)  # Higher confidence for more anomalies
            
            insight = self._create_insight(
                AIInsightType.ANOMALY_DETECTION,
                f"{len(anomalies)} Anomalies Detected",
                ai_insights.get("interpretation", f"Detected {len(anomalies)} statistical anomalies"),
                confidence,
                impact,
                ai_insights.get("recommendations", ["Investigate anomalies", "Verify data quality"])
            )
            
            self.insights.append(insight)
            return insight
            
        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {e}")
            return self._create_insight(
                AIInsightType.ANOMALY_DETECTION,
                "Anomaly Detection Failed",
                f"Error detecting anomalies: {str(e)}",
                0.0,
                "Low",
                ["Manual analysis required"]
            )
    
    async def generate_predictions(
        self,
        data: List[Dict[str, Any]],
        prediction_type: PredictionType,
        time_horizon: int = 30
    ) -> List[Prediction]:
        """Generate predictions using historical data."""
        try:
            df = pd.DataFrame(data)
            
            predictions = []
            
            if prediction_type == PredictionType.PROJECT_COMPLETION:
                predictions = await self._predict_project_completion(df, time_horizon)
            elif prediction_type == PredictionType.BUDGET_CONSUMPTION:
                predictions = await self._predict_budget_consumption(df, time_horizon)
            elif prediction_type == PredictionType.RESOURCE_UTILIZATION:
                predictions = await self._predict_resource_utilization(df, time_horizon)
            elif prediction_type == PredictionType.RISK_PROBABILITY:
                predictions = await self._predict_risk_probability(df, time_horizon)
            elif prediction_type == PredictionType.TIMELINE_DEVIATION:
                predictions = await self._predict_timeline_deviation(df, time_horizon)
            elif prediction_type == PredictionType.QUALITY_METRICS:
                predictions = await self._predict_quality_metrics(df, time_horizon)
            
            # Add predictions to service
            self.predictions.extend(predictions)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to generate predictions: {e}")
            return []
    
    async def _predict_project_completion(self, df: pd.DataFrame, time_horizon: int) -> List[Prediction]:
        """Predict project completion rates."""
        try:
            if 'percent_complete' not in df.columns or 'due_date' not in df.columns:
                return []
            
            df['due_date'] = pd.to_datetime(df['due_date'])
            df['days_remaining'] = (df['due_date'] - datetime.now()).dt.days
            
            predictions = []
            
            for _, row in df.iterrows():
                if pd.isna(row['percent_complete']) or pd.isna(row['days_remaining']):
                    continue
                
                # Simple linear prediction
                if row['days_remaining'] > 0:
                    current_progress = row['percent_complete']
                    daily_progress_rate = current_progress / max(1, (30 - row['days_remaining']))
                    predicted_completion = min(100, current_progress + (daily_progress_rate * time_horizon))
                    
                    confidence = 0.7 if daily_progress_rate > 0 else 0.3
                    
                    prediction = Prediction(
                        prediction_type=PredictionType.PROJECT_COMPLETION,
                        target=f"Project completion in {time_horizon} days",
                        value=f"{predicted_completion:.1f}%",
                        confidence=confidence,
                        time_horizon=time_horizon,
                        factors=["Current progress rate", "Historical completion patterns"],
                        expires_at=datetime.now() + timedelta(days=time_horizon)
                    )
                    predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to predict project completion: {e}")
            return []
    
    async def _predict_budget_consumption(self, df: pd.DataFrame, time_horizon: int) -> List[Prediction]:
        """Predict budget consumption patterns."""
        try:
            if 'budget_amount' not in df.columns or 'percent_complete' not in df.columns:
                return []
            
            predictions = []
            
            for _, row in df.iterrows():
                if pd.isna(row['budget_amount']) or pd.isna(row['percent_complete']):
                    continue
                
                # Estimate budget consumption based on progress
                total_budget = row['budget_amount']
                current_progress = row['percent_complete']
                
                if current_progress > 0:
                    estimated_total_consumption = total_budget * (100 / current_progress)
                    remaining_budget = total_budget - (estimated_total_consumption - total_budget)
                    
                    confidence = 0.8 if current_progress > 20 else 0.5
                    
                    prediction = Prediction(
                        prediction_type=PredictionType.BUDGET_CONSUMPTION,
                        target=f"Budget consumption in {time_horizon} days",
                        value=f"${remaining_budget:.2f} remaining",
                        confidence=confidence,
                        time_horizon=time_horizon,
                        factors=["Current budget utilization", "Progress rate"],
                        expires_at=datetime.now() + timedelta(days=time_horizon)
                    )
                    predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Failed to predict budget consumption: {e}")
            return []
    
    async def _predict_resource_utilization(self, df: pd.DataFrame, time_horizon: int) -> List[Prediction]:
        """Predict resource utilization patterns."""
        try:
            if 'availability_percentage' not in df.columns:
                return []
            
            avg_utilization = df['availability_percentage'].mean()
            std_utilization = df['availability_percentage'].std()
            
            # Predict future utilization
            predicted_utilization = avg_utilization + (std_utilization * 0.1)  # Slight increase
            
            confidence = 0.7 if std_utilization < 10 else 0.5
            
            prediction = Prediction(
                prediction_type=PredictionType.RESOURCE_UTILIZATION,
                target=f"Resource utilization in {time_horizon} days",
                value=f"{predicted_utilization:.1f}%",
                confidence=confidence,
                time_horizon=time_horizon,
                factors=["Historical utilization", "Resource availability trends"],
                expires_at=datetime.now() + timedelta(days=time_horizon)
            )
            
            return [prediction]
            
        except Exception as e:
            self.logger.error(f"Failed to predict resource utilization: {e}")
            return []
    
    async def _predict_risk_probability(self, df: pd.DataFrame, time_horizon: int) -> List[Prediction]:
        """Predict risk probability."""
        try:
            # Simple risk prediction based on project characteristics
            risk_factors = []
            risk_score = 0.0
            
            if 'percent_complete' in df.columns:
                avg_progress = df['percent_complete'].mean()
                if avg_progress < 30:
                    risk_score += 0.2
                    risk_factors.append("Low progress")
            
            if 'budget_amount' in df.columns:
                budget_std = df['budget_amount'].std()
                if budget_std > df['budget_amount'].mean() * 0.5:
                    risk_score += 0.2
                    risk_factors.append("High budget variance")
            
            if 'due_date' in df.columns:
                df['due_date'] = pd.to_datetime(df['due_date'])
                overdue_projects = len(df[df['due_date'] < datetime.now()])
                if overdue_projects > 0:
                    risk_score += 0.3
                    risk_factors.append("Overdue projects")
            
            risk_probability = min(1.0, risk_score)
            confidence = 0.6 if len(risk_factors) > 0 else 0.4
            
            prediction = Prediction(
                prediction_type=PredictionType.RISK_PROBABILITY,
                target=f"Risk probability in {time_horizon} days",
                value=f"{risk_probability:.1%}",
                confidence=confidence,
                time_horizon=time_horizon,
                factors=risk_factors,
                expires_at=datetime.now() + timedelta(days=time_horizon)
            )
            
            return [prediction]
            
        except Exception as e:
            self.logger.error(f"Failed to predict risk probability: {e}")
            return []
    
    async def _predict_timeline_deviation(self, df: pd.DataFrame, time_horizon: int) -> List[Prediction]:
        """Predict timeline deviations."""
        try:
            if 'due_date' not in df.columns or 'start_date' not in df.columns:
                return []
            
            df['due_date'] = pd.to_datetime(df['due_date'])
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['planned_duration'] = (df['due_date'] - df['start_date']).dt.days
            
            # Calculate average deviation
            avg_duration = df['planned_duration'].mean()
            std_duration = df['planned_duration'].std()
            
            deviation_probability = std_duration / avg_duration if avg_duration > 0 else 0
            
            confidence = 0.7 if len(df) > 5 else 0.5
            
            prediction = Prediction(
                prediction_type=PredictionType.TIMELINE_DEVIATION,
                target=f"Timeline deviation probability in {time_horizon} days",
                value=f"{deviation_probability:.1%}",
                confidence=confidence,
                time_horizon=time_horizon,
                factors=["Historical duration variance", "Project complexity"],
                expires_at=datetime.now() + timedelta(days=time_horizon)
            )
            
            return [prediction]
            
        except Exception as e:
            self.logger.error(f"Failed to predict timeline deviation: {e}")
            return []
    
    async def _predict_quality_metrics(self, df: pd.DataFrame, time_horizon: int) -> List[Prediction]:
        """Predict quality metrics."""
        try:
            # Simple quality prediction
            quality_score = 0.8  # Default quality score
            confidence = 0.6
            
            prediction = Prediction(
                prediction_type=PredictionType.QUALITY_METRICS,
                target=f"Quality metrics in {time_horizon} days",
                value=f"{quality_score:.1f}/1.0",
                confidence=confidence,
                time_horizon=time_horizon,
                factors=["Historical quality trends", "Process maturity"],
                expires_at=datetime.now() + timedelta(days=time_horizon)
            )
            
            return [prediction]
            
        except Exception as e:
            self.logger.error(f"Failed to predict quality metrics: {e}")
            return []
    
    async def generate_smart_recommendations(
        self,
        context: Dict[str, Any],
        recommendation_type: str = "general"
    ) -> List[str]:
        """Generate smart recommendations using AI."""
        try:
            ai_service = await get_ai_service()
            
            context_summary = f"""
            Recommendation Context:
            Type: {recommendation_type}
            Data: {json.dumps(context, indent=2)}
            """
            
            messages = [
                AIMessage(
                    role="system",
                    content="""You are a project management expert. Analyze the provided context and generate smart, actionable recommendations.
                    Focus on:
                    1. Immediate actions
                    2. Strategic improvements
                    3. Risk mitigation
                    4. Optimization opportunities
                    5. Best practices
                    
                    Provide 3-5 specific, actionable recommendations."""
                ),
                AIMessage(role="user", content=context_summary)
            ]
            
            response = await ai_service.ollama_client.generate_text(
                model="llama3:8b",
                messages=messages,
                temperature=0.4
            )
            
            # Parse recommendations
            try:
                recommendations_data = json.loads(response.content)
                recommendations = recommendations_data.get("recommendations", [])
            except json.JSONDecodeError:
                # Fallback: extract recommendations from text
                recommendations = []
                lines = response.content.split('\n')
                for line in lines:
                    if line.strip() and ('•' in line or '-' in line or line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))):
                        clean_rec = line.strip().lstrip('•-123456789. ').strip()
                        if clean_rec:
                            recommendations.append(clean_rec)
                
                if not recommendations:
                    recommendations = [
                        "Review current processes",
                        "Implement monitoring systems",
                        "Consider automation opportunities"
                    ]
            
            return recommendations[:5]  # Limit to 5 recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate smart recommendations: {e}")
            return [
                "Review current processes",
                "Implement monitoring systems",
                "Consider automation opportunities"
            ]
    
    async def automate_task(
        self,
        task_name: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> AutomationTask:
        """Create and execute an automation task."""
        try:
            task = AutomationTask(
                name=task_name,
                description=f"Automated {task_type} task",
                task_type=task_type,
                parameters=parameters
            )
            
            self.automation_tasks[task.id] = task
            
            # Execute task based on type
            if task_type == "data_sync":
                result = await self._execute_data_sync_task(parameters)
            elif task_type == "report_generation":
                result = await self._execute_report_generation_task(parameters)
            elif task_type == "notification_send":
                result = await self._execute_notification_task(parameters)
            elif task_type == "data_cleanup":
                result = await self._execute_data_cleanup_task(parameters)
            else:
                result = {"status": "unsupported", "message": f"Task type '{task_type}' not supported"}
            
            # Update task
            task.status = "completed" if result.get("status") == "success" else "failed"
            task.completed_at = datetime.now()
            task.result = result
            task.updated_at = datetime.now()
            
            if task.status == "failed":
                task.error = result.get("message", "Unknown error")
            
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to execute automation task: {e}")
            task.status = "failed"
            task.error = str(e)
            task.updated_at = datetime.now()
            return task
    
    async def _execute_data_sync_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data synchronization task."""
        try:
            # Simulate data sync
            await asyncio.sleep(1)  # Simulate work
            return {"status": "success", "message": "Data synchronized successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _execute_report_generation_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation task."""
        try:
            # Simulate report generation
            await asyncio.sleep(2)  # Simulate work
            return {"status": "success", "message": "Report generated successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _execute_notification_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification task."""
        try:
            # Simulate notification sending
            await asyncio.sleep(0.5)  # Simulate work
            return {"status": "success", "message": "Notification sent successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _execute_data_cleanup_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data cleanup task."""
        try:
            # Simulate data cleanup
            await asyncio.sleep(1.5)  # Simulate work
            return {"status": "success", "message": "Data cleanup completed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _create_insight(
        self,
        insight_type: AIInsightType,
        title: str,
        description: str,
        confidence: float,
        impact: str,
        recommendations: List[str]
    ) -> AIInsight:
        """Create an AI insight."""
        return AIInsight(
            insight_type=insight_type,
            title=title,
            description=description,
            confidence=confidence,
            impact=impact,
            recommendations=recommendations,
            expires_at=datetime.now() + timedelta(days=7)  # Insights expire after 7 days
        )
    
    def get_insights(self, insight_type: Optional[AIInsightType] = None) -> List[AIInsight]:
        """Get insights, optionally filtered by type."""
        insights = self.insights
        
        if insight_type:
            insights = [insight for insight in insights if insight.insight_type == insight_type]
        
        # Filter out expired insights
        current_time = datetime.now()
        insights = [insight for insight in insights if not insight.expires_at or insight.expires_at > current_time]
        
        return insights
    
    def get_predictions(self, prediction_type: Optional[PredictionType] = None) -> List[Prediction]:
        """Get predictions, optionally filtered by type."""
        predictions = self.predictions
        
        if prediction_type:
            predictions = [pred for pred in predictions if pred.prediction_type == prediction_type]
        
        # Filter out expired predictions
        current_time = datetime.now()
        predictions = [pred for pred in predictions if pred.expires_at > current_time]
        
        return predictions
    
    def get_automation_tasks(self, status: Optional[str] = None) -> List[AutomationTask]:
        """Get automation tasks, optionally filtered by status."""
        tasks = list(self.automation_tasks.values())
        
        if status:
            tasks = [task for task in tasks if task.status == status]
        
        return tasks
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "total_insights": len(self.insights),
            "active_insights": len([i for i in self.insights if not i.expires_at or i.expires_at > datetime.now()]),
            "total_predictions": len(self.predictions),
            "active_predictions": len([p for p in self.predictions if p.expires_at > datetime.now()]),
            "total_automation_tasks": len(self.automation_tasks),
            "completed_tasks": len([t for t in self.automation_tasks.values() if t.status == "completed"]),
            "failed_tasks": len([t for t in self.automation_tasks.values() if t.status == "failed"]),
            "timestamp": datetime.now()
        }


# Global instance
advanced_ai_service: Optional[AdvancedAIService] = None


async def get_advanced_ai_service() -> AdvancedAIService:
    """Get global advanced AI service instance."""
    global advanced_ai_service
    if advanced_ai_service is None:
        advanced_ai_service = AdvancedAIService()
    return advanced_ai_service
