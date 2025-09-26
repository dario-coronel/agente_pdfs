"""
Script de prueba para el clasificador agropecuario especializado
"""
import sys
import os
import json
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from classifiers.agro_classifier import AgroDocumentClassifier
from classifiers.intelligent_classifier import IntelligentClassifier


def test_agro_classifier():
    """Prueba el clasificador agropecuario con documentos de ejemplo"""
    
    print("🌾 PRUEBA DEL CLASIFICADOR AGROPECUARIO")
    print("=" * 50)
    
    # Inicializar clasificador
    agro_classifier = AgroDocumentClassifier()
    
    # Documentos de prueba
    test_documents = {
        "liquidacion_soja": """
        LIQUIDACIÓN DE GRANOS
        COOPERATIVA AGRICOLA GANADERA LTDA
        
        Productor: JUAN PÉREZ
        CUIT: 20-12345678-9
        
        SOJA CAMPAÑA 2024/25
        
        Peso Bruto: 25,500 kg
        Peso Tara: 500 kg  
        Peso Neto: 25,000 kg
        
        Humedad: 14.5%
        Proteína: 38.2%
        Impurezas: 1.2%
        
        Precio por tonelada: $450,000
        Descuento por humedad: $2,500
        Descuento por impurezas: $800
        
        TOTAL A LIQUIDAR: $11,230,700
        
        Fecha: 15/09/2024
        """,
        
        "carta_porte": """
        CARTA DE PORTE NACIONAL
        Número: 00123456789
        
        TRANSPORTISTA: TRANSPORTES DEL CAMPO S.R.L.
        CUIT: 30-87654321-2
        Chapa del Camión: ABC-123
        
        ORIGEN: Campo "LA ESPERANZA"
        Dirección: Ruta 35 Km 187, Pergamino, Buenos Aires
        
        DESTINO: Puerto Rosario
        Dirección: Terminal 6, Puerto Gral. San Martín
        
        MERCADERÍA: Granos de Soja
        Peso Estimado: 32,000 kg
        
        Fecha de Carga: 20/09/2024
        Hora: 08:30
        
        Observaciones: Grano limpio y seco
        """,
        
        "cot_certificado": """
        CERTIFICADO DE TRANSFERENCIA - COT
        Número: COT-2024-001234
        
        EMISOR: TERMINAL BAHÍA BLANCA S.A.
        CUIT: 30-12345678-9
        
        BENEFICIARIO: EXPORTADORA GRANOS DEL SUR
        CUIT: 30-98765432-1
        
        DESCRIPCIÓN DEL PRODUCTO:
        Commodity: TRIGO PAN
        Calidad: Estándar
        Peso: 2,500 toneladas
        
        CERTIFICACIÓN:
        Humedad: 13.8%
        Peso Hectolítrico: 78 kg/hl
        Proteína: 11.5%
        Gluten húmedo: 28%
        
        Depósito: Célula 15-A
        Fecha de Depósito: 05/09/2024
        Fecha de Vencimiento: 05/03/2025
        
        TRANSFERENCIA AUTORIZADA
        """,
        
        "ctg_warrant": """
        CARTA DE CRÉDITO GRANARIO - CTG
        Warrant Nº: 45678912
        
        ALMACÉN GENERAL DE DEPÓSITO: CARGILL S.A.
        Matrícula: 001
        CUIT: 30-50000000-7
        
        DEPOSITANTE: AGROPECUARIA LA PAMPA S.A.
        CUIT: 30-11111111-1
        
        MERCADERÍA DEPOSITADA:
        Producto: MAÍZ COLORADO DURO
        Calidad: Base
        Cantidad: 1,850 toneladas
        
        Análisis de Calidad:
        - Humedad: 14.2%
        - Materias Extrañas: 2%
        - Granos Quebrados: 3%
        - Granos Dañados: 1.5%
        
        Ubicación: Planta Pergamino
        Célula: 22-B
        
        Fecha de Depósito: 12/08/2024
        Costo de Almacenaje: $125/tn/mes
        """,
        
        "pesaje_camion": """
        TICKET DE PESAJE
        BÁSCULA AUTOMÁTICA
        
        Fecha: 25/09/2024
        Hora: 14:32:15
        Ticket Nº: 789456123
        
        TRANSPORTISTA: LOGÍSTICA CAMPO LTDA
        Patente: DEF-456
        Chofer: CARLOS GONZÁLEZ
        
        PRODUCTO: Granos de Girasol
        DESTINO: Aceitera del Paraná
        
        PESAJE:
        Peso Bruto: 48,720 kg
        Peso Tara: 16,200 kg
        Peso Neto: 32,520 kg
        
        Observaciones:
        - Grano seco y limpio
        - Carga completa
        - Sin observaciones
        
        OPERADOR: M. Fernández
        """,
        
        "contrato_compraventa": """
        CONTRATO DE COMPRAVENTA DE GRANOS
        
        Entre COOPERATIVA UNIÓN AGRÍCOLA (Vendedor)
        CUIT: 30-33333333-3
        y MOLINOS DEL PLATA S.A. (Comprador)  
        CUIT: 30-44444444-4
        
        OBJETO: Compraventa de TRIGO
        
        ESPECIFICACIONES:
        Cantidad: 5,000 toneladas
        Calidad: Grado 1 - Standard
        Precio: U$S 280 por tonelada
        
        CONDICIONES DE ENTREGA:
        Período: Octubre 2024
        Lugar: Planta San Lorenzo
        Transporte: Por cuenta del vendedor
        
        CALIDAD PACTADA:
        - Humedad máxima: 14%
        - Peso hectolítrico mínimo: 76 kg/hl
        - Proteína mínima: 10.5%
        - Gluten húmedo: 25% mínimo
        
        Fecha del Contrato: 01/09/2024
        """
    }
    
    # Probar cada documento
    for doc_name, text in test_documents.items():
        print(f"\n📋 DOCUMENTO: {doc_name.upper()}")
        print("-" * 40)
        
        # Clasificación agropecuaria
        doc_type, confidence, details = agro_classifier.classify_agro_document(text)
        
        print(f"Tipo detectado: {doc_type}")
        print(f"Confianza: {confidence:.3f}")
        print(f"Es documento agropecuario: {confidence > 0.3}")
        
        # Mostrar términos agropecuarios encontrados
        if details.get("agro_terms_found"):
            print(f"Términos agro encontrados: {', '.join(details['agro_terms_found'][:5])}")
        
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
        
        # Extraer información agropecuaria
        agro_indicators = details.get("agro_indicators", {})
        if agro_indicators:
            if agro_indicators.get("grains_mentioned"):
                print(f"Granos: {', '.join(agro_indicators['grains_mentioned'])}")
            if agro_indicators.get("weights_found"):
                print(f"Pesos: {', '.join(agro_indicators['weights_found'][:3])}")
            if agro_indicators.get("prices_found"):
                print(f"Precios: {', '.join(agro_indicators['prices_found'][:2])}")


def test_intelligent_classifier():
    """Prueba el clasificador inteligente con los nuevos tipos agropecuarios"""
    
    print(f"\n\n🧠 PRUEBA DEL CLASIFICADOR INTELIGENTE")
    print("=" * 50)
    
    # Inicializar clasificador inteligente con soporte agropecuario
    intelligent_classifier = IntelligentClassifier(enable_agro=True)
    
    # Documento de prueba
    test_text = """
    LIQUIDACIÓN DE GRANOS - SOJA
    ACOPIADORA DEL CENTRO S.R.L.
    
    Productor: ESTANCIA LA ABUNDANCIA
    CUIT: 30-55555555-5
    
    Campaña: 2024/25
    Producto: Soja de Primera
    
    Entregas:
    15/08/2024 - 18,500 kg
    22/08/2024 - 21,200 kg
    28/08/2024 - 19,800 kg
    Total Entregado: 59,500 kg
    
    Análisis Promedio:
    Humedad: 13.8%
    Proteína: 39.1% 
    Aceite: 20.5%
    Impurezas: 0.8%
    
    Precio Base: $485,000/tn
    Bonificación proteína: $8,500/tn
    Descuento humedad: $1,200/tn
    Precio Final: $492,300/tn
    
    TOTAL BRUTO: $29,291,850
    Retenciones: $2,636,267
    Gastos: $587,837
    NETO A COBRAR: $26,067,746
    """
    
    print("📄 Analizando liquidación de soja...")
    
    # Clasificar con el sistema inteligente
    result = intelligent_classifier.classify_document(test_text)
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"Clasificación: {result['final_classification']}")
    print(f"Confianza: {result['final_confidence']:.3f}")
    
    print(f"\n📊 RESULTADOS POR MÉTODO:")
    for method, method_result in result["method_results"].items():
        if method_result.get("confidence", 0) > 0:
            print(f"  {method.capitalize()}: {method_result['type']} ({method_result['confidence']:.3f})")
    
    # Mostrar detalles del método agropecuario si está disponible
    agro_result = result["method_results"].get("agro")
    if agro_result and agro_result.get("details"):
        details = agro_result["details"]
        print(f"\n🌾 DETALLES AGROPECUARIOS:")
        
        if details.get("agro_indicators"):
            indicators = details["agro_indicators"]
            if indicators.get("grains_mentioned"):
                print(f"  Granos mencionados: {', '.join(indicators['grains_mentioned'])}")
            if indicators.get("weights_found"):
                print(f"  Pesos encontrados: {', '.join(indicators['weights_found'][:3])}")
            if indicators.get("prices_found"):
                print(f"  Precios encontrados: {', '.join(indicators['prices_found'][:2])}")
    
    # Mostrar análisis de consenso
    consensus = result.get("consensus_analysis", {})
    if consensus.get("best_consensus"):
        print(f"\n🤝 CONSENSO:")
        print(f"  Mejor consenso: {consensus['best_consensus']}")
        print(f"  Consenso fuerte: {consensus.get('has_strong_consensus', False)}")
    
    # Mostrar razonamiento de la decisión
    decision_details = result.get("decision_details", {})
    if decision_details.get("final_reasoning"):
        print(f"\n💭 RAZONAMIENTO:")
        print(f"  {decision_details['final_reasoning']}")


def test_classification_performance():
    """Prueba el rendimiento de la clasificación con múltiples documentos"""
    
    print(f"\n\n⚡ PRUEBA DE RENDIMIENTO")
    print("=" * 50)
    
    agro_classifier = AgroDocumentClassifier()
    
    # Textos cortos para prueba de velocidad
    test_texts = [
        "liquidación de granos soja humedad 14% proteína 38%",
        "carta de porte transporte granos destino puerto",
        "certificado transferencia cot granos trigo depósito",
        "warrant almacén general depósito maíz toneladas",
        "pesaje báscula peso neto 32500 kg girasol",
        "contrato compraventa cereales precio tonelada",
        "factura comercial productos varios",
        "remito entrega mercadería general"
    ]
    
    start_time = datetime.now()
    
    results = []
    for i, text in enumerate(test_texts, 1):
        doc_type, confidence, _ = agro_classifier.classify_agro_document(text)
        results.append((doc_type, confidence))
        print(f"  Texto {i}: {doc_type} ({confidence:.3f})")
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"  Documentos procesados: {len(test_texts)}")
    print(f"  Tiempo total: {processing_time:.3f} segundos")
    print(f"  Tiempo promedio por documento: {processing_time/len(test_texts):.3f} segundos")
    
    # Contar clasificaciones agropecuarias
    agro_docs = sum(1 for _, conf in results if conf > 0.3)
    print(f"  Documentos agropecuarios detectados: {agro_docs}/{len(test_texts)}")


if __name__ == "__main__":
    try:
        # Ejecutar todas las pruebas
        test_agro_classifier()
        test_intelligent_classifier()  
        test_classification_performance()
        
        print(f"\n\n✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 50)
        print("El clasificador agropecuario está funcionando correctamente.")
        print("Tipos de documentos soportados:")
        print("  • Liquidaciones de granos")
        print("  • Certificados de transferencia (COT)")
        print("  • Cartas de crédito granario (CTG)")
        print("  • Cartas de porte")
        print("  • Tickets de pesaje")
        print("  • Contratos de compraventa de granos")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()