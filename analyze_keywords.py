"""
Análisis del problema de clasificación de palabras clave
"""
import sys
import os
sys.path.append('.')

from classifiers.document_classifier import DocumentClassifier
from extractors.text_extractor import TextExtractor

def analyze_keyword_classification():
    """Analiza por qué el clasificador de palabras clave detecta 'notas_credito'"""
    
    # Buscar el archivo
    pdf_path = None
    for root, dirs, files in os.walk('output_pdfs'):
        for file in files:
            if 'liquidacionDebitoCredito' in file:
                pdf_path = os.path.join(root, file)
                break

    if not pdf_path:
        print("Archivo no encontrado")
        return

    extractor = TextExtractor()
    text = extractor.extract_from_pdf(pdf_path)
    
    keyword_classifier = DocumentClassifier()
    
    # Obtener detalles de clasificación
    details = keyword_classifier.get_classification_details(text)
    
    print('=== ANÁLISIS CLASIFICADOR DE PALABRAS CLAVE ===')
    print(f'Clasificación: {details["classification"]}')
    print(f'Confianza: {details["confidence"]:.3f}')
    
    print('\nPuntuaciones por tipo:')
    for doc_type, score in details['scores'].items():
        if score > 0:
            print(f'  {doc_type}: {score:.3f}')
    
    print('\nPalabras clave encontradas:')
    for doc_type, keywords in details['keywords_found'].items():
        if keywords:
            print(f'  {doc_type}: {keywords}')
    
    # Buscar específicamente términos problemáticos
    text_lower = text.lower()
    print('\n=== BÚSQUEDA DE TÉRMINOS PROBLEMÁTICOS ===')
    
    problematic_terms = ['débito', 'debito', 'crédito', 'credito', 'nota']
    for term in problematic_terms:
        count = text_lower.count(term)
        if count > 0:
            print(f'Término "{term}": {count} ocurrencias')
    
    # Buscar específicamente las palabras de liquidación
    print('\n=== TÉRMINOS DE LIQUIDACIÓN ===')
    liquidacion_terms = ['liquidación', 'liquidacion', 'granos', 'trigo', 'cereales']
    for term in liquidacion_terms:
        count = text_lower.count(term)
        if count > 0:
            print(f'Término "{term}": {count} ocurrencias')

if __name__ == "__main__":
    analyze_keyword_classification()