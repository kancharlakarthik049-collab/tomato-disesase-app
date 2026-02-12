/// Classifier Service - TensorFlow Lite Model Integration
/// 
/// This service handles:
/// - Loading the TFLite model from assets
/// - Loading disease labels
/// - Leaf detection (green pixel analysis)
/// - Image preprocessing (resize, normalize)
/// - Running inference
/// - Parsing prediction results

import 'dart:io';
import 'dart:math' as math;
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';
import '../models/prediction_result.dart';

class ClassifierService {
  // TFLite interpreter
  Interpreter? _interpreter;
  
  // Disease labels
  List<String> _labels = [];
  
  // Model input specifications (matching Python training: 224x224, [0,1] normalization)
  static const int inputSize = 224;
  static const int numChannels = 3;
  static const int numClasses = 10;
  
  // Confidence threshold - below this, prediction is marked as "Uncertain"
  static const double confidenceThreshold = 0.6;
  
  // Minimum probability gap - if top predictions are too close, mark as uncertain
  static const double minProbabilityGap = 0.1;
  
  // Leaf detection thresholds (matching Python app.py)
  // HSV values: H is 0-360 in image library, S and V are 0-100
  static const double greenHueMin = 60;  // ~25 in 0-255 scale → 60 in 0-360
  static const double greenHueMax = 160; // ~100 in 0-255 scale → 160 in 0-360
  static const double saturationMin = 15.7; // 40/255 * 100
  static const double valueMin = 15.7;      // 40/255 * 100
  static const double greenPropThreshold = 0.03; // 3% green pixels required
  
  // Asset paths
  static const String modelPath = 'assets/tomato_disease_model.tflite';
  static const String labelsPath = 'assets/labels.txt';
  
  /// Check if the classifier is ready
  bool get isReady => _interpreter != null && _labels.isNotEmpty;
  
  /// Initialize the classifier by loading model and labels
  Future<void> initialize() async {
    await Future.wait([
      _loadModel(),
      _loadLabels(),
    ]);
    
    if (!isReady) {
      throw Exception('Failed to initialize classifier');
    }
  }
  
  /// Load TFLite model from assets
  Future<void> _loadModel() async {
    try {
      // Configure interpreter options for optimal performance
      final options = InterpreterOptions()
        ..threads = 4; // Use 4 threads for inference
      
      // Load model from assets
      _interpreter = await Interpreter.fromAsset(
        modelPath,
        options: options,
      );
      
      // Allocate tensors
      _interpreter!.allocateTensors();
      
      // Log model info
      final inputShape = _interpreter!.getInputTensor(0).shape;
      final outputShape = _interpreter!.getOutputTensor(0).shape;
      
      print('Model loaded successfully');
      print('Input shape: $inputShape');
      print('Output shape: $outputShape');
      
    } catch (e) {
      print('Error loading model: $e');
      rethrow;
    }
  }
  
  /// Load disease labels from assets
  Future<void> _loadLabels() async {
    try {
      final labelsData = await rootBundle.loadString(labelsPath);
      _labels = labelsData
          .split('\n')
          .map((label) => label.trim())
          .where((label) => label.isNotEmpty)
          .toList();
      
      print('Loaded ${_labels.length} labels');
      
    } catch (e) {
      print('Error loading labels: $e');
      rethrow;
    }
  }
  
  // ============================================================
  // DEBUG & VALIDATION FUNCTIONS
  // ============================================================
  
  /// Debug function to validate model and preprocessing pipeline
  /// Call this after initialize() to verify everything is working
  Future<Map<String, dynamic>> debugModelInfo() async {
    if (!isReady) {
      throw Exception('Classifier not initialized - call initialize() first');
    }
    
    final debugInfo = <String, dynamic>{};
    
    print('\n' + '=' * 60);
    print('🔍 MODEL DEBUG INFORMATION');
    print('=' * 60);
    
    // 1. Model tensor shapes
    final inputTensor = _interpreter!.getInputTensor(0);
    final outputTensor = _interpreter!.getOutputTensor(0);
    
    debugInfo['inputShape'] = inputTensor.shape;
    debugInfo['outputShape'] = outputTensor.shape;
    debugInfo['inputType'] = inputTensor.type.toString();
    debugInfo['outputType'] = outputTensor.type.toString();
    
    print('\n📊 MODEL TENSOR INFO:');
    print('  Input Shape: ${inputTensor.shape}');
    print('  Input Type: ${inputTensor.type}');
    print('  Output Shape: ${outputTensor.shape}');
    print('  Output Type: ${outputTensor.type}');
    
    // 2. Validate expected shapes
    final expectedInputShape = [1, inputSize, inputSize, numChannels];
    final inputShapeMatch = _listEquals(inputTensor.shape, expectedInputShape);
    debugInfo['inputShapeValid'] = inputShapeMatch;
    
    print('\n✅ SHAPE VALIDATION:');
    print('  Expected Input: $expectedInputShape');
    print('  Actual Input: ${inputTensor.shape}');
    print('  Match: ${inputShapeMatch ? "✓ YES" : "✗ NO - MISMATCH!"}');
    
    if (!inputShapeMatch) {
      print('  ⚠️ WARNING: Input shape mismatch! Update inputSize constant.');
      // Extract actual size from model
      if (inputTensor.shape.length == 4) {
        print('  → Model expects: ${inputTensor.shape[1]}x${inputTensor.shape[2]} images');
      }
    }
    
    // 3. Labels info
    debugInfo['numLabels'] = _labels.length;
    debugInfo['labels'] = _labels;
    
    print('\n🏷️ LABELS (${_labels.length} classes):');
    for (int i = 0; i < _labels.length; i++) {
      print('  [$i] ${_labels[i]}');
    }
    
    // 4. Validate label count matches output
    final outputClasses = outputTensor.shape.last;
    final labelsMatch = _labels.length == outputClasses;
    debugInfo['labelsMatchOutput'] = labelsMatch;
    
    print('\n✅ LABELS VALIDATION:');
    print('  Model output classes: $outputClasses');
    print('  Loaded labels: ${_labels.length}');
    print('  Match: ${labelsMatch ? "✓ YES" : "✗ NO - MISMATCH!"}');
    
    print('\n' + '=' * 60 + '\n');
    
    return debugInfo;
  }
  
  /// Test preprocessing with a sample image file
  /// Shows detailed pixel value information
  Future<Map<String, dynamic>> debugPreprocessing(File imageFile) async {
    print('\n' + '=' * 60);
    print('🖼️ PREPROCESSING DEBUG');
    print('=' * 60);
    
    final debugInfo = <String, dynamic>{};
    
    // 1. Load and decode image
    final imageBytes = await imageFile.readAsBytes();
    final image = img.decodeImage(imageBytes);
    
    if (image == null) {
      throw Exception('Failed to decode image');
    }
    
    debugInfo['originalWidth'] = image.width;
    debugInfo['originalHeight'] = image.height;
    debugInfo['originalChannels'] = image.numChannels;
    
    print('\n📷 ORIGINAL IMAGE:');
    print('  Size: ${image.width} x ${image.height}');
    print('  Channels: ${image.numChannels}');
    print('  Format: ${image.format}');
    
    // 2. Sample original pixel values
    final centerX = image.width ~/ 2;
    final centerY = image.height ~/ 2;
    final origPixel = image.getPixel(centerX, centerY);
    
    print('\n🎨 ORIGINAL PIXEL VALUES (center):');
    print('  R: ${origPixel.r}, G: ${origPixel.g}, B: ${origPixel.b}');
    
    // 3. Resize image
    final resizedImage = img.copyResize(
      image,
      width: inputSize,
      height: inputSize,
      interpolation: img.Interpolation.linear,
    );
    
    debugInfo['resizedWidth'] = resizedImage.width;
    debugInfo['resizedHeight'] = resizedImage.height;
    
    print('\n📐 RESIZED IMAGE:');
    print('  Size: ${resizedImage.width} x ${resizedImage.height}');
    print('  Target: $inputSize x $inputSize');
    print('  Match: ${resizedImage.width == inputSize && resizedImage.height == inputSize ? "✓ YES" : "✗ NO"}');
    
    // 4. Analyze pixel value distribution
    double minR = double.infinity, maxR = double.negativeInfinity;
    double minG = double.infinity, maxG = double.negativeInfinity;
    double minB = double.infinity, maxB = double.negativeInfinity;
    double sumR = 0, sumG = 0, sumB = 0;
    
    // Sample pixels for statistics
    for (int y = 0; y < resizedImage.height; y += 10) {
      for (int x = 0; x < resizedImage.width; x += 10) {
        final pixel = resizedImage.getPixel(x, y);
        final r = pixel.r.toDouble();
        final g = pixel.g.toDouble();
        final b = pixel.b.toDouble();
        
        minR = math.min(minR, r); maxR = math.max(maxR, r);
        minG = math.min(minG, g); maxG = math.max(maxG, g);
        minB = math.min(minB, b); maxB = math.max(maxB, b);
        sumR += r; sumG += g; sumB += b;
      }
    }
    
    final sampleCount = (resizedImage.height ~/ 10) * (resizedImage.width ~/ 10);
    
    print('\n📊 RAW PIXEL STATISTICS (before normalization):');
    print('  R: min=${minR.toStringAsFixed(1)}, max=${maxR.toStringAsFixed(1)}, avg=${(sumR/sampleCount).toStringAsFixed(1)}');
    print('  G: min=${minG.toStringAsFixed(1)}, max=${maxG.toStringAsFixed(1)}, avg=${(sumG/sampleCount).toStringAsFixed(1)}');
    print('  B: min=${minB.toStringAsFixed(1)}, max=${maxB.toStringAsFixed(1)}, avg=${(sumB/sampleCount).toStringAsFixed(1)}');
    
    // 5. Apply normalization and check ranges (matching Python: / 255.0)
    print('\n🔄 NORMALIZATION (matching Python training: [0, 1]):');
    print('  Formula: pixel / 255.0');
    
    double minNorm = double.infinity, maxNorm = double.negativeInfinity;
    
    for (int y = 0; y < resizedImage.height; y += 10) {
      for (int x = 0; x < resizedImage.width; x += 10) {
        final pixel = resizedImage.getPixel(x, y);
        final normR = pixel.r.toDouble() / 255.0;
        final normG = pixel.g.toDouble() / 255.0;
        final normB = pixel.b.toDouble() / 255.0;
        
        minNorm = math.min(minNorm, math.min(normR, math.min(normG, normB)));
        maxNorm = math.max(maxNorm, math.max(normR, math.max(normG, normB)));
      }
    }
    
    debugInfo['normalizedMin'] = minNorm;
    debugInfo['normalizedMax'] = maxNorm;
    
    print('\n📊 NORMALIZED PIXEL RANGE:');
    print('  Min: ${minNorm.toStringAsFixed(4)}');
    print('  Max: ${maxNorm.toStringAsFixed(4)}');
    print('  Expected: [0.0, 1.0]');
    print('  Valid: ${minNorm >= -0.001 && maxNorm <= 1.001 ? "✓ YES" : "✗ NO - OUT OF RANGE!"}');
    
    // 6. Show sample normalized values
    final centerPixel = resizedImage.getPixel(inputSize ~/ 2, inputSize ~/ 2);
    final normR = centerPixel.r.toDouble() / 255.0;
    final normG = centerPixel.g.toDouble() / 255.0;
    final normB = centerPixel.b.toDouble() / 255.0;
    
    print('\n🎯 CENTER PIXEL NORMALIZED:');
    print('  Original: R=${centerPixel.r}, G=${centerPixel.g}, B=${centerPixel.b}');
    print('  Normalized: R=${normR.toStringAsFixed(4)}, G=${normG.toStringAsFixed(4)}, B=${normB.toStringAsFixed(4)}');
    
    print('\n' + '=' * 60 + '\n');
    
    return debugInfo;
  }
  
  /// Run inference with full debug output
  /// Shows raw model outputs, softmax results, and all predictions
  Future<Map<String, dynamic>> debugInference(File imageFile) async {
    if (!isReady) {
      throw Exception('Classifier not initialized');
    }
    
    print('\n' + '=' * 60);
    print('🧠 INFERENCE DEBUG');
    print('=' * 60);
    
    final debugInfo = <String, dynamic>{};
    final startTime = DateTime.now();
    
    // 1. Decode image
    final imageBytes = await imageFile.readAsBytes();
    final image = img.decodeImage(imageBytes);
    if (image == null) throw Exception('Failed to decode image');
    
    // 2. Preprocess
    final inputTensor = _preprocessImage(image);
    
    // Verify input tensor shape
    print('\n📥 INPUT TENSOR:');
    print('  Shape: [${inputTensor.length}, ${inputTensor[0].length}, ${inputTensor[0][0].length}, ${inputTensor[0][0][0].length}]');
    print('  Expected: [1, $inputSize, $inputSize, $numChannels]');
    
    // 3. Prepare and run inference
    final outputTensor = List.filled(numClasses, 0.0).reshape([1, numClasses]);
    _interpreter!.run(inputTensor, outputTensor);
    
    final rawOutput = outputTensor[0];
    debugInfo['rawOutput'] = List<double>.from(rawOutput);
    
    // 4. Analyze raw output
    print('\n📤 RAW MODEL OUTPUT (logits):');
    for (int i = 0; i < rawOutput.length; i++) {
      print('  [$i] ${_labels[i].padRight(35)} : ${rawOutput[i].toStringAsFixed(6)}');
    }
    
    final rawSum = rawOutput.reduce((a, b) => a + b);
    final rawMin = rawOutput.reduce(math.min);
    final rawMax = rawOutput.reduce(math.max);
    
    print('\n📊 RAW OUTPUT STATISTICS:');
    print('  Sum: ${rawSum.toStringAsFixed(4)} (logits don\'t sum to 1)');
    print('  Min: ${rawMin.toStringAsFixed(4)}');
    print('  Max: ${rawMax.toStringAsFixed(4)}');
    
    // 5. Apply softmax
    final probabilities = _softmax(rawOutput);
    debugInfo['probabilities'] = probabilities;
    
    print('\n📤 SOFTMAX PROBABILITIES:');
    for (int i = 0; i < probabilities.length; i++) {
      final pct = (probabilities[i] * 100).toStringAsFixed(2);
      final bar = '█' * (probabilities[i] * 30).round();
      print('  [$i] ${_labels[i].padRight(35)} : ${pct.padLeft(6)}% $bar');
    }
    
    final probSum = probabilities.reduce((a, b) => a + b);
    print('\n  Sum: ${probSum.toStringAsFixed(6)} (should be ~1.0)');
    
    // 6. Find best predictions
    final sortedIndices = List.generate(probabilities.length, (i) => i)
      ..sort((a, b) => probabilities[b].compareTo(probabilities[a]));
    
    print('\n🏆 TOP 3 PREDICTIONS:');
    for (int i = 0; i < math.min(3, sortedIndices.length); i++) {
      final idx = sortedIndices[i];
      final pct = (probabilities[idx] * 100).toStringAsFixed(2);
      print('  ${i + 1}. ${_formatLabel(_labels[idx])} (${pct}%)');
    }
    
    // 7. Confidence analysis
    final bestIdx = sortedIndices[0];
    final bestConf = probabilities[bestIdx];
    final secondConf = sortedIndices.length > 1 ? probabilities[sortedIndices[1]] : 0.0;
    final gap = bestConf - secondConf;
    
    debugInfo['bestPrediction'] = _labels[bestIdx];
    debugInfo['bestConfidence'] = bestConf;
    debugInfo['confidenceGap'] = gap;
    
    print('\n🎯 CONFIDENCE ANALYSIS:');
    print('  Best: ${_formatLabel(_labels[bestIdx])} (${(bestConf * 100).toStringAsFixed(2)}%)');
    print('  Threshold: ${(confidenceThreshold * 100).toStringAsFixed(0)}%');
    print('  Passes threshold: ${bestConf >= confidenceThreshold ? "✓ YES" : "✗ NO"}');
    print('  Gap to 2nd: ${(gap * 100).toStringAsFixed(2)}%');
    print('  Min gap required: ${(minProbabilityGap * 100).toStringAsFixed(0)}%');
    print('  Passes gap check: ${gap >= minProbabilityGap ? "✓ YES" : "✗ NO"}');
    
    final inferenceTime = DateTime.now().difference(startTime).inMilliseconds;
    debugInfo['inferenceTimeMs'] = inferenceTime;
    
    print('\n⏱️ Inference time: ${inferenceTime}ms');
    print('\n' + '=' * 60 + '\n');
    
    return debugInfo;
  }
  
  /// Validate preprocessing pipeline with known test values
  /// Creates a synthetic test image to verify [0, 1] normalization
  Map<String, dynamic> validatePreprocessingPipeline() {
    print('\n' + '=' * 60);
    print('🧪 PREPROCESSING VALIDATION TEST');
    print('=' * 60);
    
    final results = <String, dynamic>{};
    
    // Create test image with known pixel values
    final testImage = img.Image(width: inputSize, height: inputSize);
    
    // Fill with specific test values for [0, 1] normalization:
    // Top-left: black (0,0,0) → should normalize to (0,0,0)
    // Center: gray (127,127,127) → should normalize to (~0.498, ~0.498, ~0.498)
    // Bottom-right: white (255,255,255) → should normalize to (1,1,1)
    
    for (int y = 0; y < inputSize; y++) {
      for (int x = 0; x < inputSize; x++) {
        if (x < inputSize ~/ 3 && y < inputSize ~/ 3) {
          testImage.setPixelRgb(x, y, 0, 0, 0);  // Black
        } else if (x > 2 * inputSize ~/ 3 && y > 2 * inputSize ~/ 3) {
          testImage.setPixelRgb(x, y, 255, 255, 255);  // White
        } else {
          testImage.setPixelRgb(x, y, 127, 127, 127);  // Gray
        }
      }
    }
    
    // Process through pipeline
    final tensor = _preprocessImage(testImage);
    
    // Check black pixel (should be 0 for [0,1] range)
    final blackPixel = tensor[0][0][0];
    final blackExpected = [0.0, 0.0, 0.0];
    
    // Check gray pixel (should be ~0.498 for [0,1] range - 127/255)
    final grayPixel = tensor[0][inputSize ~/ 2][inputSize ~/ 2];
    final grayExpected = [127.0 / 255.0, 127.0 / 255.0, 127.0 / 255.0];
    
    // Check white pixel (should be 1 for [0,1] range)
    final whitePixel = tensor[0][inputSize - 1][inputSize - 1];
    final whiteExpected = [1.0, 1.0, 1.0];
    
    print('\n🎨 TEST PIXEL VALIDATION ([0, 1] normalization):');
    print('\n  BLACK (0,0,0):');
    print('    Expected: $blackExpected');
    print('    Actual:   $blackPixel');
    print('    Valid: ${_validatePixel(blackPixel, blackExpected) ? "✓" : "✗"}');
    
    print('\n  GRAY (127,127,127):');
    print('    Expected: ~$grayExpected');
    print('    Actual:   $grayPixel');
    print('    Valid: ${_validatePixel(grayPixel, grayExpected, tolerance: 0.01) ? "✓" : "✗"}');
    
    print('\n  WHITE (255,255,255):');
    print('    Expected: $whiteExpected');
    print('    Actual:   $whitePixel');
    print('    Valid: ${_validatePixel(whitePixel, whiteExpected) ? "✓" : "✗"}');
    
    results['blackValid'] = _validatePixel(blackPixel, blackExpected);
    results['grayValid'] = _validatePixel(grayPixel, grayExpected, tolerance: 0.01);
    results['whiteValid'] = _validatePixel(whitePixel, whiteExpected);
    results['allValid'] = results['blackValid'] && results['grayValid'] && results['whiteValid'];
    
    print('\n📋 OVERALL: ${results['allValid'] ? "✓ PREPROCESSING VALID" : "✗ PREPROCESSING ISSUES DETECTED"}');
    print('\n' + '=' * 60 + '\n');
    
    return results;
  }
  
  /// Helper to validate pixel values
  bool _validatePixel(List<double> actual, List<double> expected, {double tolerance = 0.001}) {
    for (int i = 0; i < 3; i++) {
      if ((actual[i] - expected[i]).abs() > tolerance) return false;
    }
    return true;
  }
  
  /// Helper to compare lists
  bool _listEquals(List<int> a, List<int> b) {
    if (a.length != b.length) return false;
    for (int i = 0; i < a.length; i++) {
      if (a[i] != b[i]) return false;
    }
    return true;
  }
  
  /// Check if the image contains a leaf/plant by analyzing green pixels
  /// Returns true if sufficient green content is detected
  Future<bool> isLeafImage(File imageFile) async {
    try {
      final imageBytes = await imageFile.readAsBytes();
      final image = img.decodeImage(imageBytes);
      
      if (image == null) {
        return false;
      }
      
      int greenPixelCount = 0;
      int totalPixels = image.width * image.height;
      
      // Sample pixels (for performance, sample every 4th pixel)
      for (int y = 0; y < image.height; y += 2) {
        for (int x = 0; x < image.width; x += 2) {
          final pixel = image.getPixel(x, y);
          
          // Convert RGB to HSV
          final r = pixel.r / 255.0;
          final g = pixel.g / 255.0;
          final b = pixel.b / 255.0;
          
          final maxC = math.max(r, math.max(g, b));
          final minC = math.min(r, math.min(g, b));
          final delta = maxC - minC;
          
          // Calculate Hue (0-360)
          double hue = 0;
          if (delta != 0) {
            if (maxC == r) {
              hue = 60 * (((g - b) / delta) % 6);
            } else if (maxC == g) {
              hue = 60 * (((b - r) / delta) + 2);
            } else {
              hue = 60 * (((r - g) / delta) + 4);
            }
          }
          if (hue < 0) hue += 360;
          
          // Calculate Saturation (0-100)
          final saturation = maxC == 0 ? 0.0 : (delta / maxC) * 100;
          
          // Calculate Value (0-100)
          final value = maxC * 100;
          
          // Check if pixel is in green range
          if (hue >= greenHueMin && hue <= greenHueMax &&
              saturation >= saturationMin && value >= valueMin) {
            greenPixelCount++;
          }
        }
      }
      
      // Adjust total for sampling (every 2nd pixel in x and y)
      final sampledPixels = (image.width ~/ 2) * (image.height ~/ 2);
      final greenProportion = greenPixelCount / sampledPixels.toDouble();
      
      print('Green proportion: ${(greenProportion * 100).toStringAsFixed(2)}%');
      
      return greenProportion >= greenPropThreshold;
    } catch (e) {
      print('Leaf detection error: $e');
      return false;
    }
  }
  
  /// Apply softmax to convert logits to probabilities
  List<double> _softmax(List<dynamic> logits) {
    // Find max for numerical stability
    double maxLogit = logits[0].toDouble();
    for (var logit in logits) {
      if (logit.toDouble() > maxLogit) {
        maxLogit = logit.toDouble();
      }
    }
    
    // Compute exp(x - max) for numerical stability
    List<double> expValues = logits.map((logit) {
      return math.exp(logit.toDouble() - maxLogit);
    }).toList();
    
    // Sum of all exp values
    double sumExp = expValues.reduce((a, b) => a + b);
    
    // Normalize to get probabilities
    return expValues.map((e) => e / sumExp).toList();
  }
  
  /// Classify an image and return prediction result
  Future<PredictionResult> classifyImage(File imageFile) async {
    if (!isReady) {
      throw Exception('Classifier not initialized');
    }
    
    final startTime = DateTime.now();
    
    // Read and decode image
    final imageBytes = await imageFile.readAsBytes();
    final image = img.decodeImage(imageBytes);
    
    if (image == null) {
      throw Exception('Failed to decode image');
    }
    
    // Preprocess image
    final inputTensor = _preprocessImage(image);
    
    // Prepare output tensor
    final outputTensor = List.filled(numClasses, 0.0).reshape([1, numClasses]);
    
    // Run inference
    _interpreter!.run(inputTensor, outputTensor);
    
    // Get raw output (logits)
    final rawOutput = outputTensor[0];
    
    // Debug: print raw output
    print('Raw model output (logits): $rawOutput');
    print('Raw output sum: ${rawOutput.reduce((a, b) => a + b)}');
    
    // Apply softmax to convert logits to probabilities
    final probabilities = _softmax(rawOutput);
    
    // Debug: print probabilities after softmax
    print('After softmax: $probabilities');
    print('Probabilities sum (should be ~1.0): ${probabilities.reduce((a, b) => a + b)}');
    
    // Find best prediction
    int bestIndex = 0;
    double bestConfidence = probabilities[0];
    
    for (int i = 1; i < probabilities.length; i++) {
      if (probabilities[i] > bestConfidence) {
        bestConfidence = probabilities[i];
        bestIndex = i;
      }
    }
    
    // Sort indices by probability for top predictions
    final sortedIndices = List.generate(probabilities.length, (i) => i)
      ..sort((a, b) => probabilities[b].compareTo(probabilities[a]));
    
    // Check confidence thresholds
    bool isUncertain = false;
    String finalLabel;
    
    // Check if confidence is too low
    if (bestConfidence < confidenceThreshold) {
      isUncertain = true;
      print('Prediction uncertain: confidence $bestConfidence < threshold $confidenceThreshold');
    }
    
    // Check if top two predictions are too close
    if (sortedIndices.length >= 2) {
      double secondBest = probabilities[sortedIndices[1]];
      double gap = bestConfidence - secondBest;
      if (gap < minProbabilityGap) {
        isUncertain = true;
        print('Prediction uncertain: gap $gap < minimum $minProbabilityGap');
      }
    }
    
    if (isUncertain) {
      finalLabel = 'Uncertain - Please try another image';
    } else {
      finalLabel = _formatLabel(_labels[bestIndex]);
    }
    
    final endTime = DateTime.now();
    final inferenceTime = endTime.difference(startTime).inMilliseconds;
    
    // Get top 3 predictions
    final topPredictions = sortedIndices.take(3).map((index) {
      return MapEntry(_formatLabel(_labels[index]), probabilities[index]);
    }).toList();
    
    return PredictionResult(
      label: finalLabel,
      confidence: bestConfidence,
      isHealthy: !isUncertain && _labels[bestIndex].toLowerCase().contains('healthy'),
      inferenceTimeMs: inferenceTime,
      topPredictions: topPredictions,
      isUncertain: isUncertain,
    );
  }
  
  /// Preprocess image to match Python training preprocessing
  /// - Resize to 224x224 (matching Python: img.resize((224, 224)))
  /// - Convert to RGB
  /// - Normalize to [0, 1] range (matching Python: / 255.0)
  List<List<List<List<double>>>> _preprocessImage(img.Image image) {
    // Resize image to model input size (224x224 - matching Python training)
    final resizedImage = img.copyResize(
      image,
      width: inputSize,
      height: inputSize,
      interpolation: img.Interpolation.linear,
    );
    
    // Debug: print sample pixel values to verify normalization
    final samplePixel = resizedImage.getPixel(inputSize ~/ 2, inputSize ~/ 2);
    print('Sample pixel RGB: ${samplePixel.r}, ${samplePixel.g}, ${samplePixel.b}');
    
    // Create input tensor with shape [1, 224, 224, 3]
    final inputTensor = List.generate(
      1,
      (_) => List.generate(
        inputSize,
        (y) => List.generate(
          inputSize,
          (x) {
            final pixel = resizedImage.getPixel(x, y);
            
            // Match Python preprocessing: img_array / 255.0
            // This normalizes pixels from [0, 255] to [0, 1]
            final r = pixel.r.toDouble() / 255.0;
            final g = pixel.g.toDouble() / 255.0;
            final b = pixel.b.toDouble() / 255.0;
            
            return [r, g, b];
          },
        ),
      ),
    );
    
    return inputTensor;
  }
  
  /// Format label for display
  /// Converts "Tomato___Early_blight" to "Early Blight"
  String _formatLabel(String label) {
    return label
        .replaceAll('Tomato___', '')
        .replaceAll('_', ' ')
        .split(' ')
        .map((word) => word.isNotEmpty 
            ? '${word[0].toUpperCase()}${word.substring(1).toLowerCase()}'
            : '')
        .join(' ')
        .trim();
  }
  
  /// Release resources
  void dispose() {
    _interpreter?.close();
    _interpreter = null;
  }
}

/// Extension to reshape List to multi-dimensional array
extension ListReshape<T> on List<T> {
  List<List<T>> reshape(List<int> shape) {
    if (shape.length != 2) {
      throw ArgumentError('reshape only supports 2D reshaping');
    }
    
    final rows = shape[0];
    final cols = shape[1];
    
    if (length != rows * cols) {
      throw ArgumentError(
        'Cannot reshape list of length $length into shape $shape'
      );
    }
    
    return List.generate(
      rows,
      (i) => sublist(i * cols, (i + 1) * cols),
    );
  }
}
