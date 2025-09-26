#!/usr/bin/env python3
"""
Test de debug del clasificador comercial.
"""

import sys
sys.path.append('.')

from classifiers.intelligent_classifier import IntelligentClassifier

def test_debug():
    print("🔍 Iniciando test de debug del clasificador comercial...")
    
    # Crear clasificador inteligente
    try:
        classifier = IntelligentClassifier()
        print("✅ Clasificador inteligente creado exitosamente")
        
        # Verificar pesos
        print(f"Pesos configurados: {classifier.classification_weights}")
        
        # Texto de prueba para comercial
        test_text = "ORDEN DE PAGO número 123 para pago de servicios por importe de $50000"
        print(f"\n📄 Texto de prueba: {test_text}")
        
        # Clasificar
        result = classifier.classify_document(test_text, "test.txt")
        
        print(f"\n🎯 Resultado final:")
        print(f"Clasificación: {result['final_classification']}")
        print(f"Confianza: {result['final_confidence']:.3f}")
        
        # Debug detallado
        print(f"\n📊 Resultados por método:")
        for method, method_result in result.get('method_results', {}).items():
            print(f"  {method}: {method_result['type']} ({method_result['confidence']:.3f})")
        
        print(f"\n⚖️ Contribuciones ponderadas:")
        for method, contrib in result.get('decision_details', {}).get('method_contributions', {}).items():
            print(f"  {method}: {contrib['contribution']:.3f} = {contrib['confidence']:.3f} * {contrib['weight']}")
        
        print(f"\n🎯 Puntajes finales por tipo:")
        final_scores = result.get('decision_details', {}).get('weighted_scores', {})
        for doc_type, score in sorted(final_scores.items(), key=lambda x: x[1], reverse=True):
            print(f"  {doc_type}: {score:.3f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_debug()