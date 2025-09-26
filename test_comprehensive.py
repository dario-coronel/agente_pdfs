#!/usr/bin/env python3
"""
Test completo de clasificadores especializados.
"""

import sys
sys.path.append('.')

from classifiers.intelligent_classifier import IntelligentClassifier

def test_comprehensive():
    print("🎯 TEST COMPLETO DE CLASIFICADORES ESPECIALIZADOS")
    print("=" * 60)
    
    classifier = IntelligentClassifier()
    
    # Casos de prueba variados
    test_cases = [
        # Documentos agropecuarios
        ("LIQUIDACION DE SOJA - Lote 123 - Precio: $450/tn - Peso: 25000kg - Humedad: 14%", "agropecuario"),
        ("CARTA DE PORTE N° 456 - Transporte de granos de soja desde campo hasta puerto", "agropecuario"),
        ("COT Certificado de Transferencia - Granos de trigo - 30 toneladas", "agropecuario"),
        
        # Documentos comerciales
        ("ORDEN DE PAGO N° 789 - Importe: $125,000 - Concepto: Pago servicios profesionales", "comercial"),
        ("TRANSFERENCIA BANCARIA - CBU: 1234567890 - Monto: $85,500 - Destino: Cuenta corriente", "comercial"),
        ("CHEQUE N° 001234 - Banco Nación - Importe: $45,000 - Fecha: 15/12/2024", "comercial"),
        
        # Documentos mixtos/otros
        ("FACTURA N° 001-0012345 - Cliente: Juan Pérez - Total: $25,000", "otros"),
        ("REMITO N° 456 - Entrega de mercaderías varias", "otros")
    ]
    
    for i, (text, expected_category) in enumerate(test_cases, 1):
        print(f"\n📄 CASO {i}: {expected_category.upper()}")
        print("-" * 50)
        print(f"Texto: {text[:60]}...")
        
        result = classifier.classify_document(text)
        classification = result['final_classification']
        confidence = result['final_confidence']
        
        print(f"🎯 Resultado: {classification} (confianza: {confidence:.3f})")
        
        # Mostrar contribuciones principales
        method_results = result.get('method_results', {})
        print("📊 Métodos principales:")
        
        for method, data in method_results.items():
            if data['confidence'] > 0.1:  # Solo métodos con confianza significativa
                print(f"  • {method}: {data['type']} ({data['confidence']:.3f})")
        
        # Verificar si la clasificación es apropiada
        agro_types = ['liquidaciones_granos', 'cartas_porte', 'cot', 'ctg', 'pesajes', 'contratos_granos']
        commercial_types = ['transferencias', 'ordenes_pago', 'cheques', 'recibos_pago', 'estados_cuenta']
        
        success = False
        if expected_category == "agropecuario" and classification in agro_types:
            success = True
        elif expected_category == "comercial" and classification in commercial_types:
            success = True
        elif expected_category == "otros" and classification not in agro_types and classification not in commercial_types:
            success = True
            
        status = "✅" if success else "❌"
        print(f"{status} Categorización: {'Correcta' if success else 'Incorrecta'}")
    
    print(f"\n{'=' * 60}")
    print("🎉 TEST COMPLETADO")

if __name__ == "__main__":
    test_comprehensive()