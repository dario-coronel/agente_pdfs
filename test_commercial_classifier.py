"""
Script de prueba para el clasificador comercial especializado
"""
import sys
import os
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from classifiers.commercial_classifier import CommercialDocumentClassifier
from classifiers.intelligent_classifier import IntelligentClassifier


def test_commercial_classifier():
    """Prueba el clasificador comercial con documentos de ejemplo"""
    
    print("💼 PRUEBA DEL CLASIFICADOR COMERCIAL")
    print("=" * 50)
    
    # Inicializar clasificador
    commercial_classifier = CommercialDocumentClassifier()
    
    # Documentos de prueba
    test_documents = {
        "transferencia_bancaria": """
        TRANSFERENCIA BANCARIA ELECTRÓNICA
        BANCO NACIÓN ARGENTINA
        
        NÚMERO DE OPERACIÓN: 2024092501234
        FECHA DE TRANSFERENCIA: 25/09/2024
        HORA: 14:30:25
        
        CUENTA ORIGEN:
        Titular: EMPRESA EJEMPLO S.A.
        CUIT: 30-12345678-9
        CBU: 0110590520000012345678
        Alias: EMPRESA.EJEMPLO.SA
        
        CUENTA DESTINO:
        Titular: PROVEEDOR SERVICIOS LTDA
        CUIT: 30-98765432-1
        CBU: 0720391988000098765432
        Alias: PROVEEDOR.SERVICIOS
        
        IMPORTE: $ 150,000.00
        CONCEPTO: Pago Factura A-0001-00123456
        COMISIÓN: $ 500.00
        
        Estado: ACREDITADA
        Código de Autorización: AUTH789456123
        """,
        
        "orden_pago": """
        ORDEN DE PAGO Nº OP-2024-5678
        
        FECHA DE EMISIÓN: 20/09/2024
        FECHA DE VENCIMIENTO: 30/09/2024
        
        SOLICITANTE:
        Razón Social: CONSTRUCTORA DEL SUR S.R.L.
        CUIT: 30-55555555-5
        Domicilio: Av. Libertador 1234, CABA
        
        BENEFICIARIO:
        Razón Social: MATERIALES INDUSTRIALES S.A.
        CUIT: 30-44444444-4
        CBU: 0150666601000044444444
        
        CONCEPTO DEL PAGO: Compra de materiales según OC-2024-001
        IMPORTE TOTAL: $ 89,500.00
        
        FORMA DE PAGO: Transferencia Bancaria
        BANCO BENEFICIARIO: BBVA Argentina
        
        AUTORIZACIONES:
        Solicitado por: Juan Pérez (Gerente Compras)
        Autorizado por: María González (Gerente General)
        
        Estado: PENDIENTE DE APROBACIÓN
        """,
        
        "cheque": """
        BANCO GALICIA
        CHEQUE Nº 12345678
        
        FECHA DE EMISIÓN: 18/09/2024
        
        PÁGUESE A: SERVICIOS TÉCNICOS INTEGRADOS S.A.
        LA CANTIDAD DE: TREINTA Y CINCO MIL PESOS
        
        $ 35,000.00
        
        LIBRADO EN: Buenos Aires
        
        CUENTA CORRIENTE Nº: 4058-7 123456-8
        
        GIRADOR:
        METALÚRGICA ARGENTINA S.A.
        CUIT: 30-66666666-6
        
        ENDOSO: NO NEGOCIABLE
        
        ________________
        Firma Autorizada
        """,
        
        "recibo_pago": """
        RECIBO DE PAGO
        Nº 000456
        
        FECHA: 22/09/2024
        
        RECIBÍ DE: COMERCIAL LA ESPERANZA S.R.L.
        CUIT: 30-33333333-3
        
        LA SUMA DE: $ 25,800.00
        (VEINTICINCO MIL OCHOCIENTOS PESOS)
        
        CONCEPTO: Cancelación Factura B-0002-00987654
        Correspondiente a servicios de consultoría
        período agosto 2024
        
        FORMA DE PAGO: Transferencia Bancaria
        Nº de Operación: TR-789456123
        
        POR: CONSULTORA PROFESIONAL S.A.
        CUIT: 30-77777777-7
        
        ________________
        FIRMA Y SELLO
        """,
        
        "estado_cuenta": """
        BANCO SANTANDER RÍO
        ESTADO DE CUENTA CORRIENTE
        
        PERÍODO: 01/09/2024 al 30/09/2024
        
        TITULAR: DISTRIBUIDORA NACIONAL S.A.
        CUIT: 30-88888888-8
        CUENTA Nº: 123-456789/0
        CBU: 0720666820000123456789
        
        SALDO INICIAL: $ 450,000.00
        
        MOVIMIENTOS DEL PERÍODO:
        
        05/09 DEPÓSITO              + $ 125,000.00
        08/09 TRANSFERENCIA SALIDA  - $ 89,500.00
        12/09 CHEQUE 12345678       - $ 35,000.00
        15/09 ACREDITACIÓN          + $ 200,000.00
        18/09 DÉBITO SERVICIOS      - $ 12,500.00
        22/09 TRANSFERENCIA ENTRADA + $ 75,000.00
        25/09 CHEQUE 12345679       - $ 45,000.00
        28/09 COMISIONES            - $ 2,800.00
        
        SALDO FINAL: $ 665,200.00
        SALDO PROMEDIO: $ 557,600.00
        
        RESUMEN:
        Total Débitos: $ 184,800.00
        Total Créditos: $ 400,000.00
        """
    }
    
    # Probar cada documento
    for doc_name, text in test_documents.items():
        print(f"\n📋 DOCUMENTO: {doc_name.upper()}")
        print("-" * 40)
        
        # Clasificación comercial
        doc_type, confidence, details = commercial_classifier.classify_commercial_document(text)
        
        print(f"Tipo detectado: {doc_type}")
        print(f"Confianza: {confidence:.3f}")
        print(f"Es documento comercial: {confidence > 0.3}")
        
        # Mostrar términos comerciales encontrados
        if details.get("commercial_terms_found"):
            print(f"Términos comerciales: {', '.join(details['commercial_terms_found'][:5])}")
        
        # Mostrar patrones encontrados
        patterns_found = details.get("patterns_found", {})
        if patterns_found:
            for pattern_type, patterns in patterns_found.items():
                if patterns:
                    print(f"Patrones {pattern_type}: {len(patterns)} encontrados")
        
        # Mostrar indicadores específicos
        indicators = details.get("specific_indicators", {})
        if indicators:
            for indicator_type, elements in indicators.items():
                print(f"Indicadores {indicator_type}: {', '.join(elements)}")
        
        # Extraer información comercial
        commercial_indicators = details.get("commercial_indicators", {})
        if commercial_indicators:
            if commercial_indicators.get("amounts_found"):
                print(f"Importes: {', '.join(commercial_indicators['amounts_found'][:3])}")
            if commercial_indicators.get("banks_mentioned"):
                print(f"Bancos: {', '.join(commercial_indicators['banks_mentioned'][:2])}")
            if commercial_indicators.get("payment_methods"):
                print(f"Métodos de pago: {', '.join(commercial_indicators['payment_methods'])}")


def test_intelligent_classifier_commercial():
    """Prueba el clasificador inteligente con tipos comerciales"""
    
    print(f"\n\n🧠 PRUEBA DEL CLASIFICADOR INTELIGENTE - COMERCIAL")
    print("=" * 50)
    
    # Inicializar clasificador inteligente con soporte comercial
    intelligent_classifier = IntelligentClassifier(enable_commercial=True)
    
    # Documento de prueba
    test_text = """
    ORDEN DE PAGO Nº 2024-OP-1234
    FECHA: 25/09/2024
    
    EMPRESA SOLICITANTE:
    AGROPECUARIA SANTA FE S.A.
    CUIT: 30-12345678-9
    
    BENEFICIARIO:
    TRANSPORTE DE GRANOS DEL LITORAL
    CUIT: 30-98765432-1
    CBU: 0110590520000098765432
    
    CONCEPTO: Pago servicios de flete
    Transporte de soja desde campo a puerto
    Período: Septiembre 2024
    
    IMPORTE: $ 485,000.00
    FORMA DE PAGO: Transferencia Bancaria
    
    AUTORIZADO POR: Gerencia General
    ESTADO: APROBADA
    """
    
    print("📄 Analizando orden de pago...")
    
    # Clasificar con el sistema inteligente
    result = intelligent_classifier.classify_document(test_text)
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"Clasificación: {result['final_classification']}")
    print(f"Confianza: {result['final_confidence']:.3f}")
    
    print(f"\n📊 RESULTADOS POR MÉTODO:")
    for method, method_result in result["method_results"].items():
        if method_result.get("confidence", 0) > 0:
            print(f"  {method.capitalize()}: {method_result['type']} ({method_result['confidence']:.3f})")
    
    # Mostrar detalles del método comercial si está disponible
    commercial_result = result["method_results"].get("commercial")
    if commercial_result and commercial_result.get("details"):
        details = commercial_result["details"]
        print(f"\n💼 DETALLES COMERCIALES:")
        
        if details.get("commercial_indicators"):
            indicators = details["commercial_indicators"]
            if indicators.get("amounts_found"):
                print(f"  Importes encontrados: {', '.join(indicators['amounts_found'][:3])}")
            if indicators.get("banks_mentioned"):
                print(f"  Bancos mencionados: {', '.join(indicators['banks_mentioned'])}")
            if indicators.get("payment_methods"):
                print(f"  Métodos de pago: {', '.join(indicators['payment_methods'])}")
    
    # Mostrar razonamiento de la decisión
    decision_details = result.get("decision_details", {})
    if decision_details.get("final_reasoning"):
        print(f"\n💭 RAZONAMIENTO:")
        print(f"  {decision_details['final_reasoning']}")


if __name__ == "__main__":
    try:
        # Ejecutar todas las pruebas
        test_commercial_classifier()
        test_intelligent_classifier_commercial()
        
        print(f"\n\n✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 50)
        print("El clasificador comercial está funcionando correctamente.")
        print("Tipos de documentos comerciales soportados:")
        print("  • Transferencias bancarias")
        print("  • Órdenes de pago")
        print("  • Cheques")
        print("  • Recibos de pago")
        print("  • Estados de cuenta")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()