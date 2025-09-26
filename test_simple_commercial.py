"""
Test simple del clasificador inteligente con comercial
"""
import sys
sys.path.append('.')

from classifiers.intelligent_classifier import IntelligentClassifier

def test_simple():
    try:
        # Crear clasificador con todos los métodos habilitados
        classifier = IntelligentClassifier(
            enable_ml=True, 
            enable_layout=True, 
            enable_agro=True, 
            enable_commercial=True
        )
        
        print("✅ Clasificador inteligente creado exitosamente")
        print(f"Pesos configurados: {classifier.classification_weights}")
        
        # Texto simple para prueba
        test_text = "ORDEN DE PAGO número 123 para pago de servicios por importe de $50000"
        
        print(f"\n📄 Texto de prueba: {test_text}")
        
        # Clasificar
        result = classifier.classify_document(test_text)
        
        print(f"\n🎯 Resultado:")
        print(f"Clasificación: {result['final_classification']}")
        print(f"Confianza: {result['final_confidence']:.3f}")
        
        print(f"\n📊 Métodos ejecutados:")
        for method, method_result in result["method_results"].items():
            conf = method_result.get("confidence", 0)
            doc_type = method_result.get("type", "N/A")
            print(f"  {method}: {doc_type} ({conf:.3f})")
        
        if "error" in result:
            print(f"\n❌ Error encontrado: {result['error']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()