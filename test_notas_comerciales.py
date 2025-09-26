#!/usr/bin/env python3
"""
Test del clasificador comercial con notas de crédito y débito.
"""

import sys
sys.path.append('.')

from classifiers.commercial_classifier import CommercialDocumentClassifier
from classifiers.intelligent_classifier import IntelligentClassifier

def test_notas_credito_debito():
    print("🔍 TEST DE NOTAS DE CRÉDITO Y DÉBITO")
    print("=" * 60)
    
    # Crear clasificadores
    commercial_classifier = CommercialDocumentClassifier()
    intelligent_classifier = IntelligentClassifier()
    
    # Casos de prueba
    test_cases = [
        # Notas de Crédito
        {
            "text": "NOTA DE CRÉDITO N° 001-00012345 - Devolución por producto defectuoso - Importe: $25,000 - Cliente: Juan Pérez S.A.",
            "expected_type": "notas_credito",
            "description": "Nota de crédito por devolución"
        },
        {
            "text": "Credit Note #CN-2024-456 - Reintegro por cancelación de servicios - Amount: USD 1,200",
            "expected_type": "notas_credito", 
            "description": "Credit note en inglés"
        },
        {
            "text": "Bonificación especial por inconvenientes - Crédito a favor del cliente - Monto: $15,000",
            "expected_type": "notas_credito",
            "description": "Bonificación/crédito"
        },
        
        # Notas de Débito
        {
            "text": "NOTA DE DÉBITO N° 002-00067890 - Cargo por interés por mora - Importe: $3,500 - Vencimiento: 30/09/2024",
            "expected_type": "notas_debito",
            "description": "Nota de débito por interés"
        },
        {
            "text": "Debit Note DN-789 - Cargo adicional por servicios extra - Amount: $850 - Account: 1234567890",
            "expected_type": "notas_debito",
            "description": "Debit note en inglés"
        },
        {
            "text": "Recargo por gastos administrativos - Comisión bancaria - Débito en cuenta corriente: $450",
            "expected_type": "notas_debito",
            "description": "Recargo/débito"
        }
    ]
    
    print("🧪 PRUEBA DEL CLASIFICADOR COMERCIAL ESPECIALIZADO")
    print("-" * 50)
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📄 Test {i}: {case['description']}")
        print(f"Texto: {case['text'][:60]}...")
        
        # Clasificación comercial especializada
        doc_type, confidence, details = commercial_classifier.classify_commercial_document(case['text'])
        
        print(f"🎯 Resultado Comercial: {doc_type} (confianza: {confidence:.3f})")
        
        # Verificar si es correcto
        is_correct = doc_type == case['expected_type']
        status = "✅" if is_correct else "❌"
        print(f"{status} Esperado: {case['expected_type']} | Obtenido: {doc_type}")
        
        if is_correct:
            success_count += 1
            
        # Mostrar patrones encontrados
        patterns_found = details.get('patterns_found', {}).get(doc_type, [])
        if patterns_found:
            if isinstance(patterns_found, list):
                print(f"   📊 Patrones encontrados: {len(patterns_found)}")
            else:
                print(f"   📊 Patrones encontrados: {patterns_found}")
    
    print(f"\n🧠 PRUEBA DEL CLASIFICADOR INTELIGENTE INTEGRADO")
    print("-" * 50)
    
    intelligent_success = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📄 Test {i}: {case['description']}")
        
        # Clasificación inteligente (incluye comercial)
        result = intelligent_classifier.classify_document(case['text'])
        classification = result['final_classification']
        confidence = result['final_confidence']
        
        print(f"🎯 Resultado Inteligente: {classification} (confianza: {confidence:.3f})")
        
        # Verificar si es correcto
        is_correct = classification == case['expected_type']
        status = "✅" if is_correct else "❌"
        print(f"{status} Esperado: {case['expected_type']} | Obtenido: {classification}")
        
        if is_correct:
            intelligent_success += 1
            
        # Mostrar contribución del clasificador comercial
        method_results = result.get('method_results', {})
        commercial_result = method_results.get('commercial')
        if commercial_result:
            print(f"   💼 Contribución comercial: {commercial_result['type']} ({commercial_result['confidence']:.3f})")
    
    print(f"\n{'=' * 60}")
    print(f"📊 RESUMEN DE RESULTADOS")
    print(f"Clasificador Comercial: {success_count}/{total_tests} correctos ({success_count/total_tests*100:.1f}%)")
    print(f"Clasificador Inteligente: {intelligent_success}/{total_tests} correctos ({intelligent_success/total_tests*100:.1f}%)")
    
    if success_count == total_tests and intelligent_success == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
    else:
        print("⚠️  Algunos tests fallaron - revisar implementación")

if __name__ == "__main__":
    test_notas_credito_debito()