"""
Clasificador básico de Machine Learning usando TF-IDF y Naive Bayes
"""
import os
import pickle
import logging
import numpy as np
from typing import Dict, Tuple, List, Optional
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import sqlite3
from config import DOCUMENT_TYPES

logger = logging.getLogger(__name__)


class MLClassifier:
    """Clasificador de Machine Learning básico usando TF-IDF y Naive Bayes"""
    
    def __init__(self, model_path: str = "ml_models/document_classifier.pkl"):
        self.model_path = model_path
        self.pipeline = None
        self.is_trained = False
        self.min_samples_per_class = 5  # Mínimo de muestras por clase para entrenar
        
        # Configuración del pipeline ML
        self.vectorizer_params = {
            'max_features': 5000,
            'stop_words': self._get_spanish_stopwords(),
            'ngram_range': (1, 2),  # Unigrams y bigrams
            'min_df': 2,  # Mínimo 2 documentos para considerar una palabra
            'max_df': 0.8  # Máximo 80% de documentos
        }
        
        self._ensure_model_directory()
        self._load_model()
    
    def _get_spanish_stopwords(self) -> List[str]:
        """Retorna lista de stopwords en español para documentos comerciales"""
        return [
            'de', 'la', 'que', 'el', 'en', 'y', 'a', 'un', 'ser', 'se',
            'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para',
            'al', 'del', 'los', 'una', 'las', 'por', 'como', 'más', 'este',
            'total', 'subtotal', 'iva', 'neto', 'fecha', 'numero', 'código',
            'descripción', 'cantidad', 'precio', 'importe'
        ]
    
    def _ensure_model_directory(self):
        """Crea el directorio para modelos si no existe"""
        model_dir = os.path.dirname(self.model_path)
        if model_dir:
            os.makedirs(model_dir, exist_ok=True)
    
    def _load_model(self):
        """Carga el modelo entrenado si existe"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                self.is_trained = True
                logger.info("Modelo ML cargado exitosamente")
            else:
                logger.info("No se encontró modelo entrenado")
        except Exception as e:
            logger.error(f"Error cargando modelo ML: {e}")
            self.pipeline = None
            self.is_trained = False
    
    def _save_model(self):
        """Guarda el modelo entrenado"""
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.pipeline, f)
            logger.info(f"Modelo ML guardado en {self.model_path}")
        except Exception as e:
            logger.error(f"Error guardando modelo ML: {e}")
    
    def _get_training_data(self) -> Tuple[List[str], List[str]]:
        """
        Obtiene datos de entrenamiento desde la base de datos
        
        Returns:
            Tuple con (textos, etiquetas)
        """
        texts = []
        labels = []
        
        try:
            # Aquí necesitaríamos una tabla adicional con textos completos
            # Por ahora, usamos datos sintéticos basados en patrones conocidos
            training_samples = self._generate_synthetic_training_data()
            
            for sample in training_samples:
                texts.append(sample['text'])
                labels.append(sample['label'])
            
            logger.info(f"Datos de entrenamiento obtenidos: {len(texts)} muestras")
            return texts, labels
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de entrenamiento: {e}")
            return [], []
    
    def _generate_synthetic_training_data(self) -> List[Dict]:
        """
        Genera datos de entrenamiento sintéticos basados en patrones conocidos
        Esta es una implementación temporal hasta tener datos reales
        """
        synthetic_data = []
        
        # Ejemplos sintéticos para cada tipo de documento
        examples = {
            "facturas": [
                "FACTURA A N° 0001-00012345 ORIGINAL DUPLICADO CUIT: 20-12345678-9 PUNTO DE VENTA: 0001 CAE N°: 12345678901234 VENCIMIENTO DEL CAE: 31/12/2024 CÓDIGO DESCRIPCIÓN CANTIDAD PRECIO UNITARIO IMPORTE 001 PRODUCTO A 1 100.00 100.00 SUBTOTAL $ 100.00 IVA 21% $ 21.00 TOTAL $ 121.00",
                "FACTURA B N° 0002-00067890 MONOTRIBUTISTA CUIT: 27-87654321-3 DETALLE CANTIDAD P.UNIT TOTAL SERVICIO DE CONSULTORIA 1 5000.00 5000.00 TOTAL $ 5000.00",
                "ORIGINAL FACTURA A PUNTO DE VENTA 0005 N° 00000123 FECHA 15/09/2024 CUIT 30-12345678-9 RESPONSABLE INSCRIPTO ITEM DESCRIPCIÓN CANT P.UNIT NETO 1 MERCADERÍA VARIA 10 50.00 500.00 SUBTOTAL 500.00 IVA 21% 105.00 TOTAL 605.00"
            ],
            "remitos": [
                "REMITO N° 0001-00012345 DOCUMENTO NO VÁLIDO COMO FACTURA DESTINATARIO: EMPRESA ABC SA CUIT: 30-11111111-1 CÓDIGO ARTÍCULO CANTIDAD 001 PRODUCTO A 5 002 PRODUCTO B 3 MERCADERÍA ENTREGADA SIN CARGO FISCAL",
                "ORDEN DE ENTREGA N° R-12345 BULTOS: 3 PESO: 25 KG DESTINATARIO JUAN PEREZ MERCADERÍA ENTREGADA CONFORME FIRMA TRANSPORTISTA",
                "REMITO INTERNO N° 0005-00000789 SIN CARGO FISCAL CÓDIGO DESCRIPCIÓN CANTIDAD ENTREGADA 100 ARTÍCULO VARIOS 15 200 MATERIAL OFICINA 8 TOTAL BULTOS: 2"
            ],
            "notas_credito": [
                "NOTA DE CRÉDITO A N° 0001-00000123 CUIT: 20-12345678-9 ANULACIÓN PARCIAL FACTURA N° 0001-00012340 CONCEPTO: DEVOLUCIÓN MERCADERÍA DEFECTUOSA IMPORTE A FAVOR $ 100.00 CRÉDITO FISCAL IVA $ 21.00",
                "NOTA DE CREDITO B N° 0002-00000456 MONOTRIBUTISTA DESCUENTO OTORGADO POR PAGO ANTICIPADO FACTURA ORIGINAL N° 0002-00067800 IMPORTE ORIGINAL $ 1000.00 DESCUENTO $ 50.00 NUEVO TOTAL $ 950.00",
                "NC A N° 0003-00000789 DEVOLUCIÓN TOTAL FACTURA N° 0003-00001200 MOTIVO: ERROR EN FACTURACIÓN IMPORTE A FAVOR DEL CLIENTE $ 500.00"
            ],
            "notas_debito": [
                "NOTA DE DÉBITO A N° 0001-00000123 CUIT: 20-12345678-9 CARGO ADICIONAL CONCEPTO: INTERESES MORATORIOS POR PAGO FUERA DE TÉRMINO FACTURA VENCIDA N° 0001-00012300 DÉBITO FISCAL $ 50.00",
                "NOTA DE DEBITO B N° 0002-00000456 GASTOS ADMINISTRATIVOS POR GESTIÓN DE COBRANZA FACTURA ORIGINAL N° 0002-00067700 CARGO ADICIONAL $ 25.00",
                "ND A N° 0003-00000789 AJUSTE DE PRECIO POR VARIACIÓN EN COSTOS FACTURA BASE N° 0003-00001100 DIFERENCIA A COBRAR $ 75.00"
            ],
            "cartas_porte": [
                "CARTA DE PORTE N° CP-12345 TRANSPORTISTA: TRANSPORTE RÁPIDO SA CUIT: 30-22222222-2 CONDUCTOR: JOSÉ GARCÍA DNI: 12345678 PATENTE CHASIS: ABC123 ACOPLADO: DEF456 ORIGEN: BUENOS AIRES DESTINO: CÓRDOBA KM RECORRIDOS: 700",
                "CARTA PORTE NACIONAL N° 0001-00000123 MERCADERÍA A TRANSPORTAR: ALIMENTOS SECOS PESO BRUTO: 15000 KG TRANSPORTISTA HABILITADO CONDUCTOR AUTORIZADO RUTA: RN9",
                "CP N° 789654 TRANSPORTE DE CARGA GENERAL ORIGEN ROSARIO DESTINO MENDOZA CONDUCTOR LUIS MARTINEZ PATENTE HGI789 KM ESTIMADOS 580"
            ],
            "recibos": [
                "RECIBO N° R-001234 RECIBÍ DE: EMPRESA XYZ SA LA SUMA DE: PESOS CINCO MIL CON 00/100 ($5.000,00) EN CONCEPTO DE: SEÑA CONTRATO DE ALQUILER OFICINA PERÍODO: OCTUBRE 2024 FIRMA Y ACLARACIÓN",
                "RECIBO OFICIAL N° 000123 RECIBIMOS DE JUAN PÉREZ LA CANTIDAD DE $ 1.500,00 PESOS UN MIL QUINIENTOS CON 00/100 POR CONCEPTO DE HONORARIOS PROFESIONALES FECHA 15/09/2024",
                "COMPROBANTE DE PAGO N° 456789 RECIBÍ LA SUMA DE $ 2.000 PESOS DOS MIL EN EFECTIVO CONCEPTO ANTICIPO SERVICIOS VARIOS FIRMA RESPONSABLE"
            ]
        }
        
        for doc_type, texts in examples.items():
            for text in texts:
                synthetic_data.append({
                    'text': text,
                    'label': doc_type
                })
        
        return synthetic_data
    
    def train_model(self, force_retrain: bool = False) -> Dict:
        """
        Entrena el modelo de Machine Learning
        
        Args:
            force_retrain: Forzar reentrenamiento aunque ya exista modelo
            
        Returns:
            Diccionario con métricas del entrenamiento
        """
        if self.is_trained and not force_retrain:
            logger.info("Modelo ya entrenado, usar force_retrain=True para reentrenar")
            return {"status": "already_trained"}
        
        try:
            # Obtener datos de entrenamiento
            texts, labels = self._get_training_data()
            
            if len(texts) == 0:
                logger.warning("No hay datos de entrenamiento disponibles")
                return {"status": "no_data"}
            
            # Verificar que hay suficientes muestras por clase
            label_counts = Counter(labels)
            insufficient_classes = [
                label for label, count in label_counts.items() 
                if count < self.min_samples_per_class
            ]
            
            if insufficient_classes:
                logger.warning(f"Clases con pocas muestras: {insufficient_classes}")
            
            # Crear pipeline
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(**self.vectorizer_params)),
                ('classifier', MultinomialNB(alpha=1.0))
            ])
            
            # Dividir datos para validación si hay suficientes muestras
            if len(texts) >= 20:  # Mínimo para división
                X_train, X_test, y_train, y_test = train_test_split(
                    texts, labels, test_size=0.2, random_state=42, stratify=labels
                )
            else:
                X_train, y_train = texts, labels
                X_test, y_test = texts, labels  # Usar mismos datos para test
            
            # Entrenar modelo
            self.pipeline.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred = self.pipeline.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Guardar modelo
            self._save_model()
            self.is_trained = True
            
            metrics = {
                "status": "trained",
                "accuracy": accuracy,
                "samples_total": len(texts),
                "samples_train": len(X_train),
                "samples_test": len(X_test),
                "classes": list(label_counts.keys()),
                "class_distribution": dict(label_counts)
            }
            
            logger.info(f"Modelo entrenado exitosamente. Precisión: {accuracy:.3f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error entrenando modelo ML: {e}")
            return {"status": "error", "error": str(e)}
    
    def classify_by_ml(self, text: str) -> Tuple[str, float]:
        """
        Clasifica documento usando Machine Learning
        
        Args:
            text: Texto del documento
            
        Returns:
            Tuple con (tipo_documento, confidence_score)
        """
        if not self.is_trained or self.pipeline is None:
            logger.warning("Modelo ML no entrenado, intentando entrenamiento automático")
            train_result = self.train_model()
            
            if train_result.get("status") != "trained":
                logger.warning("No se pudo entrenar el modelo ML")
                return "desconocido", 0.0
        
        try:
            # Predecir clase
            predicted_class = self.pipeline.predict([text])[0]
            
            # Obtener probabilidades para calcular confianza
            probabilities = self.pipeline.predict_proba([text])[0]
            confidence = np.max(probabilities)
            
            logger.debug(f"Clasificación ML: {predicted_class} (confianza: {confidence:.3f})")
            return predicted_class, confidence
            
        except Exception as e:
            logger.error(f"Error en clasificación ML: {e}")
            return "desconocido", 0.0
    
    def get_feature_importance(self, doc_type: str, top_features: int = 20) -> List[Tuple[str, float]]:
        """
        Obtiene las características más importantes para un tipo de documento
        
        Args:
            doc_type: Tipo de documento
            top_features: Número de características principales a mostrar
            
        Returns:
            Lista de tuplas (característica, importancia)
        """
        if not self.is_trained or self.pipeline is None:
            return []
        
        try:
            # Obtener vocabulario del vectorizador
            feature_names = self.pipeline.named_steps['tfidf'].get_feature_names_out()
            
            # Obtener coeficientes del clasificador
            classifier = self.pipeline.named_steps['classifier']
            classes = classifier.classes_
            
            if doc_type not in classes:
                return []
            
            class_idx = np.where(classes == doc_type)[0][0]
            coefficients = classifier.feature_log_prob_[class_idx]
            
            # Obtener top características
            top_indices = np.argsort(coefficients)[-top_features:][::-1]
            top_features_list = [
                (feature_names[idx], coefficients[idx]) 
                for idx in top_indices
            ]
            
            return top_features_list
            
        except Exception as e:
            logger.error(f"Error obteniendo importancia de características: {e}")
            return []
    
    def get_classification_probabilities(self, text: str) -> Dict[str, float]:
        """
        Obtiene probabilidades de clasificación para todas las clases
        
        Args:
            text: Texto del documento
            
        Returns:
            Diccionario con probabilidades por clase
        """
        if not self.is_trained or self.pipeline is None:
            return {}
        
        try:
            classes = self.pipeline.named_steps['classifier'].classes_
            probabilities = self.pipeline.predict_proba([text])[0]
            
            return dict(zip(classes, probabilities))
            
        except Exception as e:
            logger.error(f"Error obteniendo probabilidades: {e}")
            return {}
    
    def retrain_with_feedback(self, text: str, correct_label: str):
        """
        Reentrana el modelo con retroalimentación
        Esta funcionalidad permitiría aprendizaje incremental
        
        Args:
            text: Texto del documento
            correct_label: Etiqueta correcta proporcionada por el usuario
        """
        # Esta funcionalidad se puede implementar más adelante
        # para permitir aprendizaje incremental del modelo
        logger.info(f"Retroalimentación registrada: {correct_label}")
        pass