/// Home Screen - Professional UI for TomatoCare Disease Detection
/// 
/// Modern, professional interface featuring:
/// - Gradient backgrounds
/// - Animated elements
/// - Glass-morphism cards
/// - Smooth transitions

import 'dart:io';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/classifier_service.dart';
import '../models/prediction_result.dart';
import '../widgets/image_preview_widget.dart';
import '../widgets/prediction_result_widget.dart';
import '../widgets/action_buttons_widget.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  // Classifier service for TFLite model inference
  late ClassifierService _classifierService;
  
  // Animation controller
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  
  // Image picker instance
  final ImagePicker _imagePicker = ImagePicker();
  
  // State variables
  File? _selectedImage;
  PredictionResult? _predictionResult;
  bool _isLoading = false;
  bool _isModelLoading = true;
  String? _errorMessage;
  
  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
    _initializeClassifier();
  }
  
  /// Initialize the TFLite classifier
  Future<void> _initializeClassifier() async {
    try {
      _classifierService = ClassifierService();
      await _classifierService.initialize();
      
      if (mounted) {
        setState(() {
          _isModelLoading = false;
        });
        _animationController.forward();
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isModelLoading = false;
          _errorMessage = 'Failed to load AI model: $e';
        });
      }
    }
  }
  
  /// Pick image from camera
  Future<void> _pickImageFromCamera() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.camera,
        imageQuality: 90,
        maxWidth: 1024,
        maxHeight: 1024,
      );
      
      if (image != null) {
        _processImage(File(image.path));
      }
    } catch (e) {
      _showError('Camera error: $e');
    }
  }
  
  /// Pick image from gallery
  Future<void> _pickImageFromGallery() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 90,
        maxWidth: 1024,
        maxHeight: 1024,
      );
      
      if (image != null) {
        _processImage(File(image.path));
      }
    } catch (e) {
      _showError('Gallery error: $e');
    }
  }
  
  /// Process the selected image and run inference
  Future<void> _processImage(File imageFile) async {
    setState(() {
      _selectedImage = imageFile;
      _predictionResult = null;
      _errorMessage = null;
      _isLoading = true;
    });
    
    try {
      // Check if image contains a leaf
      final isLeaf = await _classifierService.isLeafImage(imageFile);
      
      if (!isLeaf) {
        if (mounted) {
          setState(() {
            _isLoading = false;
            _errorMessage = 'No tomato leaf detected. Please capture a clear image of a tomato leaf.';
          });
        }
        return;
      }
      
      // Run classification
      final result = await _classifierService.classifyImage(imageFile);
      
      if (mounted) {
        setState(() {
          _predictionResult = result;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _errorMessage = 'Analysis failed: $e';
        });
      }
    }
  }
  
  /// Clear current selection
  void _clearSelection() {
    setState(() {
      _selectedImage = null;
      _predictionResult = null;
      _errorMessage = null;
    });
  }
  
  /// Show error snackbar
  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.error_outline, color: Colors.white),
            const SizedBox(width: 12),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: const Color(0xFFE74C3C),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        margin: const EdgeInsets.all(16),
      ),
    );
  }
  
  @override
  void dispose() {
    _animationController.dispose();
    _classifierService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: _buildAppBar(),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF1A1A2E),
              Color(0xFF16213E),
              Color(0xFF0F3460),
            ],
          ),
        ),
        child: SafeArea(
          child: _isModelLoading
              ? _buildLoadingModelView()
              : FadeTransition(
                  opacity: _fadeAnimation,
                  child: _buildMainContent(),
                ),
        ),
      ),
    );
  }
  
  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      flexibleSpace: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              const Color(0xFF2ECC71).withOpacity(0.8),
              const Color(0xFF27AE60).withOpacity(0.6),
            ],
          ),
        ),
      ),
      title: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.eco, color: Colors.white, size: 24),
          ),
          const SizedBox(width: 12),
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'TomatoCare',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: 0.5,
                ),
              ),
              Text(
                'AI Plant Doctor',
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.white70,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
        ],
      ),
      actions: [
        // Debug button
        Container(
          margin: const EdgeInsets.only(right: 4),
          child: IconButton(
            icon: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.orange.withOpacity(0.3),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.bug_report, color: Colors.orange, size: 20),
            ),
            tooltip: 'Debug Model',
            onPressed: _runDebugTests,
          ),
        ),
        if (_selectedImage != null)
          Container(
            margin: const EdgeInsets.only(right: 8),
            child: IconButton(
              icon: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.refresh, color: Colors.white, size: 20),
              ),
              tooltip: 'New Scan',
              onPressed: _clearSelection,
            ),
          ),
      ],
    );
  }
  
  /// Run debug tests for model validation
  Future<void> _runDebugTests() async {
    // Show debug dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1A1A2E),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Row(
          children: [
            Icon(Icons.bug_report, color: Colors.orange),
            SizedBox(width: 10),
            Text('Debug Tests', style: TextStyle(color: Colors.white)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Running debug tests...\nCheck console output (logcat) for detailed results.',
              style: TextStyle(color: Colors.white70),
            ),
            const SizedBox(height: 20),
            FutureBuilder(
              future: _performDebugTests(),
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(
                    child: CircularProgressIndicator(color: Colors.orange),
                  );
                }
                if (snapshot.hasError) {
                  return Text(
                    'Error: ${snapshot.error}',
                    style: const TextStyle(color: Colors.red),
                  );
                }
                final results = snapshot.data as Map<String, dynamic>?;
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildDebugResult('Model loaded', results?['modelValid'] ?? false),
                    _buildDebugResult('Input shape valid', results?['inputShapeValid'] ?? false),
                    _buildDebugResult('Labels loaded', results?['labelsValid'] ?? false),
                    _buildDebugResult('Preprocessing valid', results?['preprocessingValid'] ?? false),
                    const SizedBox(height: 10),
                    Text(
                      'Input: ${results?['inputShape'] ?? 'N/A'}',
                      style: const TextStyle(color: Colors.white54, fontSize: 12),
                    ),
                    Text(
                      'Labels: ${results?['numLabels'] ?? 0} classes',
                      style: const TextStyle(color: Colors.white54, fontSize: 12),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close', style: TextStyle(color: Colors.orange)),
          ),
          if (_selectedImage != null)
            TextButton(
              onPressed: () async {
                Navigator.of(context).pop();
                await _runInferenceDebug();
              },
              child: const Text('Debug Inference', style: TextStyle(color: Colors.green)),
            ),
        ],
      ),
    );
  }
  
  Future<Map<String, dynamic>> _performDebugTests() async {
    final results = <String, dynamic>{};
    
    try {
      // 1. Debug model info
      final modelInfo = await _classifierService.debugModelInfo();
      results['modelValid'] = true;
      results['inputShape'] = modelInfo['inputShape']?.toString();
      results['inputShapeValid'] = modelInfo['inputShapeValid'] ?? false;
      results['labelsValid'] = (modelInfo['numLabels'] ?? 0) > 0;
      results['numLabels'] = modelInfo['numLabels'];
      
      // 2. Validate preprocessing
      final preprocResults = _classifierService.validatePreprocessingPipeline();
      results['preprocessingValid'] = preprocResults['allValid'] ?? false;
      
    } catch (e) {
      results['modelValid'] = false;
      results['error'] = e.toString();
    }
    
    return results;
  }
  
  Future<void> _runInferenceDebug() async {
    if (_selectedImage == null) return;
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Running inference debug... Check console output'),
        backgroundColor: Colors.orange,
      ),
    );
    
    try {
      // Run preprocessing debug
      await _classifierService.debugPreprocessing(_selectedImage!);
      
      // Run inference debug
      await _classifierService.debugInference(_selectedImage!);
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Debug complete! Check console for detailed output.'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Debug error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  Widget _buildDebugResult(String label, bool valid) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(
            valid ? Icons.check_circle : Icons.cancel,
            color: valid ? Colors.green : Colors.red,
            size: 20,
          ),
          const SizedBox(width: 10),
          Text(label, style: const TextStyle(color: Colors.white)),
        ],
      ),
    );
  }
  
  /// Build loading view while model is initializing
  Widget _buildLoadingModelView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Animated logo
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0.8, end: 1.0),
            duration: const Duration(milliseconds: 1000),
            curve: Curves.easeInOut,
            builder: (context, value, child) {
              return Transform.scale(
                scale: value,
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF2ECC71), Color(0xFF27AE60)],
                    ),
                    borderRadius: BorderRadius.circular(30),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF2ECC71).withOpacity(0.4),
                        blurRadius: 30,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.eco,
                    size: 60,
                    color: Colors.white,
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 40),
          const Text(
            'TomatoCare',
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: Colors.white,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Initializing AI Engine...',
            style: TextStyle(
              fontSize: 16,
              color: Colors.white.withOpacity(0.7),
            ),
          ),
          const SizedBox(height: 40),
          SizedBox(
            width: 200,
            child: LinearProgressIndicator(
              backgroundColor: Colors.white.withOpacity(0.2),
              valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF2ECC71)),
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        ],
      ),
    );
  }
  
  /// Build main content area
  Widget _buildMainContent() {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Image preview section
          ImagePreviewWidget(
            imageFile: _selectedImage,
            isLoading: _isLoading,
          ),
          
          const SizedBox(height: 24),
          
          // Error message
          if (_errorMessage != null) ...[
            _buildErrorCard(),
            const SizedBox(height: 20),
          ],
          
          // Prediction results
          if (_predictionResult != null && !_isLoading) ...[
            PredictionResultWidget(result: _predictionResult!),
            const SizedBox(height: 24),
          ],
          
          // Action buttons
          ActionButtonsWidget(
            onCameraPressed: _pickImageFromCamera,
            onGalleryPressed: _pickImageFromGallery,
            isEnabled: !_isLoading,
          ),
          
          const SizedBox(height: 24),
          
          // Instructions card
          if (_selectedImage == null)
            _buildInstructionsCard(),
            
          // Stats section when no image
          if (_selectedImage == null) ...[
            const SizedBox(height: 20),
            _buildStatsRow(),
          ],
        ],
      ),
    );
  }
  
  /// Build error card
  Widget _buildErrorCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFFE74C3C).withOpacity(0.2),
            const Color(0xFFC0392B).withOpacity(0.1),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFFE74C3C).withOpacity(0.5),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFFE74C3C).withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.warning_amber_rounded,
              color: Color(0xFFE74C3C),
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              _errorMessage!,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  /// Build instructions card
  Widget _buildInstructionsCard() {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.white.withOpacity(0.1),
                Colors.white.withOpacity(0.05),
              ],
            ),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: Colors.white.withOpacity(0.2),
              width: 1,
            ),
          ),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2ECC71), Color(0xFF27AE60)],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Icon(
                  Icons.lightbulb_outline,
                  size: 32,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'How It Works',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 16),
              _buildInstructionStep(1, 'Capture or select a tomato leaf image'),
              _buildInstructionStep(2, 'AI analyzes the leaf for diseases'),
              _buildInstructionStep(3, 'Get instant diagnosis with confidence'),
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFF2ECC71).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Row(
                  children: [
                    Icon(
                      Icons.tips_and_updates,
                      color: Color(0xFF2ECC71),
                      size: 20,
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'For best results, ensure good lighting and a clear leaf image',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildInstructionStep(int number, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF2ECC71), Color(0xFF27AE60)],
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                '$number',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 15,
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildStatsRow() {
    return Row(
      children: [
        Expanded(child: _buildStatCard('10', 'Diseases', Icons.bug_report)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('AI', 'Powered', Icons.psychology)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('Fast', 'Analysis', Icons.speed)),
      ],
    );
  }
  
  Widget _buildStatCard(String value, String label, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withOpacity(0.1),
            Colors.white.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.1),
        ),
      ),
      child: Column(
        children: [
          Icon(icon, color: const Color(0xFF2ECC71), size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.white.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }
}
