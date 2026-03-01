# ai/inference.py

class MLFilter:
    """
    Заглушка для ML-фільтра.
    Можна підключити XGBoost / sklearn модель пізніше.
    """

    def __init__(self, model_path: str, threshold: float = 0.5):
        self.model_path = model_path
        self.threshold = threshold
        self.model = None  # тут можна завантажити модель

    def allow(self, features) -> bool:
        """
        Повертає True/False, чи дозволяти угоду.
        Зараз просто завжди True.
        """
        return True
