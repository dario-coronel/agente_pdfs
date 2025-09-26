"""
Script para reprocesat el documento con el clasificador inteligente corregido
"""
import sys
import os
sys.path.append('.')

from classifiers.intelligent_classifier import IntelligentClassifier
from extractors.text_extractor import TextExtractor

def test_corrected_classifier():
    """Prueba el clasificador inteligente con umbral corregido"""
    
    print("🔧 PROBANDO CLASIFICADOR INTELIGENTE CORREGIDO")
    print("=" * 50)
    
    # Buscar el archivo PDF
    pdf_path = None
    for root, dirs, files in os.walk('output_pdfs'):
        for file in files:
            if 'liquidacionDebitoCredito' in file:
                pdf_path = os.path.join(root, file)
                break
    
    if not pdf_path:
        print("❌ Archivo no encontrado")
        return
    
    print(f"📄 Procesando: {pdf_path}")
    
    # Extraer texto
    extractor = TextExtractor()
    text = extractor.extract_from_pdf(pdf_path)
    
    # Clasificar con el clasificador inteligente corregido
    intelligent_classifier = IntelligentClassifier(enable_agro=True)
    result = intelligent_classifier.classify_document(text)
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"Clasificación: {result['final_classification']}")
    print(f"Confianza: {result['final_confidence']:.3f}")
    print(f"Umbral mínimo: {intelligent_classifier.min_confidence_threshold}")
    
    print(f"\n📊 RESULTADOS POR MÉTODO:")
    method_results = result["method_results"]
    for method, method_result in method_results.items():
        conf = method_result.get("confidence", 0)
        doc_type = method_result.get("type", "N/A")
        if conf > 0:
            weight = intelligent_classifier.classification_weights.get(method, 0)
            contribution = conf * weight
            print(f"  {method.capitalize()}: {doc_type} (conf: {conf:.3f}, peso: {weight:.2f}, contribución: {contribution:.3f})")
    
    # Análisis de consenso
    consensus = result.get("consensus_analysis", {})
    if consensus.get("best_consensus"):
        print(f"\n🤝 CONSENSO:")
        print(f"  Mejor consenso: {consensus['best_consensus']}")
        print(f"  Consenso fuerte: {consensus.get('has_strong_consensus', False)}")
        
        # Mostrar estadísticas de consenso
        consensus_stats = consensus.get("consensus_stats", {})
        best_consensus = consensus["best_consensus"]
        if best_consensus in consensus_stats:
            stats = consensus_stats[best_consensus]
            print(f"  Votos: {stats['vote_count']}")
            print(f"  Confianza promedio: {stats['avg_confidence']:.3f}")
            print(f"  Métodos que apoyan: {', '.join(stats['supporting_methods'])}")
    
    # Detalles de decisión
    decision_details = result.get("decision_details", {})
    if decision_details.get("final_reasoning"):
        print(f"\n💭 RAZONAMIENTO:")
        print(f"  {decision_details['final_reasoning']}")
    
    # Información del proveedor
    supplier_info = result.get("supplier_info", {})
    if supplier_info.get("supplier_id"):
        print(f"\n🏢 PROVEEDOR DETECTADO:")
        print(f"  ID: {supplier_info['supplier_id']}")
        print(f"  Confianza: {supplier_info.get('confidence', 0):.3f}")
    
    # Detalles agropecuarios específicos
    agro_result = method_results.get("agro")
    if agro_result and agro_result.get("details"):
        agro_details = agro_result["details"]
        print(f"\n🌾 DETALLES AGROPECUARIOS:")
        print(f"  Es documento agropecuario: {agro_result.get('is_agro_document', False)}")
        
        agro_indicators = agro_details.get("agro_indicators", {})
        if agro_indicators.get("grains_mentioned"):
            print(f"  Granos mencionados: {', '.join(agro_indicators['grains_mentioned'])}")
        if agro_indicators.get("weights_found"):
            weights_found = agro_indicators['weights_found'][:5]  # Primeros 5
            print(f"  Pesos encontrados: {', '.join(weights_found)}")
        if agro_indicators.get("prices_found"):
            prices_found = agro_indicators['prices_found'][:3]  # Primeros 3
            print(f"  Precios encontrados: {', '.join(prices_found)}")
    
    print(f"\n✅ RESULTADO:")
    if result['final_classification'] == "liquidaciones_granos":
        print("🎉 ¡CLASIFICACIÓN CORRECTA! El documento fue identificado como liquidación de granos")
    elif result['final_classification'] == "desconocido":
        print("⚠️  Aún se clasifica como desconocido - revisar umbrales")
    else:
        print(f"🤔 Clasificado como: {result['final_classification']} - revisar lógica")


if __name__ == "__main__":
    test_corrected_classifier()