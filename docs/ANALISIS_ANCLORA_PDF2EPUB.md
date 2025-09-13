# Análisis Pipeline Técnico

Se incorpora `technical_pipeline` para mejorar la conversión de documentos con tablas o fórmulas.

- **pdf2htmlEX** transforma el PDF en HTML conservando la estructura de tablas.
- **pypandoc --mathml** genera EPUB con soporte MathML, preservando símbolos matemáticos.

`SequenceEvaluator` recomienda este pipeline cuando el análisis detecta tablas o caracteres matemáticos, optimizando la fidelidad de documentos técnicos.
