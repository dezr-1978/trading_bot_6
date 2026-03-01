# ai/model.py

import xgboost as xgb
import pandas as pd
from loguru import logger
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from ai.features import FEATURE_COLUMNS


class MLModel:
    """
    Обгортка над XGBoost для трейдингу.
    Підтримує:
    - тренування
    - інференс
    - збереження/завантаження
    """

    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = 4,
        learning_rate: float = 0.05,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
    ):
        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=-1,
        )

    # ============================================================
    # TRAINING
    # ============================================================

    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """
        Тренує модель на фічах.
        X — DataFrame з колонками FEATURE_COLUMNS.
        y — Series з 0/1.
        """

        try:
            X = X[FEATURE_COLUMNS]
        except Exception:
            logger.error("[ML] Missing required feature columns")
            raise

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )

        logger.info("[ML] Training model...")
        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)
        report = classification_report(y_test, preds)
        logger.info("\n" + report)

    # ============================================================
    # INFERENCE
    # ============================================================

    def predict_proba(self, X: pd.DataFrame) -> float:
        """
        Повертає probability класу 1 (UP).
        Використовується MLFilter.
        """

        if X is None or X.empty:
            logger.warning("[ML] Empty feature DataFrame")
            return 0.0

        try:
            X = X[FEATURE_COLUMNS]
        except Exception:
            logger.error("[ML] Missing required feature columns")
            return 0.0

        try:
            prob = self.model.predict_proba(X)[-1][1]
            return float(prob)
        except Exception:
            logger.exception("[ML] Prediction failed")
            return 0.0

    # ============================================================
    # SAVE / LOAD
    # ============================================================

    def save(self, path: str):
        try:
            self.model.save_model(path)
            logger.info(f"[ML] Model saved to {path}")
        except Exception:
            logger.exception("[ML] Failed to save model")

    def load(self, path: str):
        try:
            self.model.load_model(path)
            logger.info(f"[ML] Model loaded from {path}")
        except Exception:
            logger.exception("[ML] Failed to load model")
