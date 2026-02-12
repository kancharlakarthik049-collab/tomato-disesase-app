/// Prediction Result Model
/// 
/// Data class representing the result of disease classification

class PredictionResult {
  /// The predicted disease label (formatted)
  final String label;
  
  /// Confidence score (0.0 to 1.0)
  final double confidence;
  
  /// Whether the prediction indicates a healthy plant
  final bool isHealthy;
  
  /// Time taken for inference in milliseconds
  final int inferenceTimeMs;
  
  /// Top predictions with confidence scores
  final List<MapEntry<String, double>> topPredictions;
  
  /// Whether the prediction is uncertain (low confidence or ambiguous)
  final bool isUncertain;
  
  const PredictionResult({
    required this.label,
    required this.confidence,
    required this.isHealthy,
    required this.inferenceTimeMs,
    required this.topPredictions,
    this.isUncertain = false,
  });
  
  /// Confidence as percentage string
  String get confidencePercentage => '${(confidence * 100).toStringAsFixed(1)}%';
  
  /// Inference time formatted string
  String get inferenceTimeFormatted => '${inferenceTimeMs}ms';
  
  /// Get confidence level category
  ConfidenceLevel get confidenceLevel {
    if (isUncertain) return ConfidenceLevel.uncertain;
    if (confidence >= 0.8) return ConfidenceLevel.high;
    if (confidence >= 0.5) return ConfidenceLevel.medium;
    return ConfidenceLevel.low;
  }
  
  @override
  String toString() {
    return 'PredictionResult(label: $label, confidence: $confidencePercentage, '
           'isHealthy: $isHealthy, isUncertain: $isUncertain, time: $inferenceTimeFormatted)';
  }
}

/// Confidence level categories
enum ConfidenceLevel {
  high,
  medium,
  low,
  uncertain,
}

/// Extension for confidence level helpers
extension ConfidenceLevelExtension on ConfidenceLevel {
  String get displayName {
    switch (this) {
      case ConfidenceLevel.high:
        return 'High Confidence';
      case ConfidenceLevel.medium:
        return 'Medium Confidence';
      case ConfidenceLevel.low:
        return 'Low Confidence';
      case ConfidenceLevel.uncertain:
        return 'Uncertain';
    }
  }
}