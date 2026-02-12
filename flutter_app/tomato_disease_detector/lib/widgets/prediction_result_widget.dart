/// Prediction Result Widget - Professional Dark Theme
/// 
/// Modern disease prediction display with gradients and animations

import 'dart:ui';
import 'package:flutter/material.dart';
import '../models/prediction_result.dart';

class PredictionResultWidget extends StatelessWidget {
  final PredictionResult result;
  
  const PredictionResultWidget({
    super.key,
    required this.result,
  });

  @override
  Widget build(BuildContext context) {
    // Colors based on health status
    final bool isHealthy = result.isHealthy;
    final Color primaryColor = isHealthy 
        ? const Color(0xFF2ECC71) 
        : const Color(0xFFE74C3C);
    final Color secondaryColor = isHealthy 
        ? const Color(0xFF27AE60) 
        : const Color(0xFFC0392B);
    final IconData statusIcon = isHealthy 
        ? Icons.check_circle_rounded 
        : Icons.warning_rounded;

    return ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                primaryColor.withOpacity(0.2),
                secondaryColor.withOpacity(0.1),
              ],
            ),
            borderRadius: BorderRadius.circular(24),
            border: Border.all(
              color: primaryColor.withOpacity(0.5),
              width: 2,
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header row
                Row(
                  children: [
                    // Status icon with glow
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [primaryColor, secondaryColor],
                        ),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: primaryColor.withOpacity(0.4),
                            blurRadius: 15,
                            spreadRadius: 2,
                          ),
                        ],
                      ),
                      child: Icon(
                        statusIcon,
                        color: Colors.white,
                        size: 28,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 10,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: primaryColor.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              isHealthy ? 'HEALTHY' : 'DISEASE DETECTED',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: primaryColor,
                                letterSpacing: 1,
                              ),
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            result.label,
                            style: const TextStyle(
                              fontSize: 22,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // Confidence section
                _buildConfidenceSection(primaryColor),
                
                const SizedBox(height: 20),
                
                // Inference time
                Row(
                  children: [
                    Icon(
                      Icons.speed_rounded,
                      size: 18,
                      color: Colors.white.withOpacity(0.5),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Analysis time: ${result.inferenceTimeFormatted}',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.white.withOpacity(0.5),
                      ),
                    ),
                  ],
                ),
                
                // Top predictions (if more than one)
                if (result.topPredictions.length > 1) ...[
                  const SizedBox(height: 20),
                  _buildTopPredictions(primaryColor),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildConfidenceSection(Color accentColor) {
    final confidence = result.confidence;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Confidence Level',
              style: TextStyle(
                fontSize: 14,
                color: Colors.white.withOpacity(0.7),
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [accentColor, accentColor.withOpacity(0.7)],
                ),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                result.confidencePercentage,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        // Animated progress bar
        Container(
          height: 10,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(5),
          ),
          child: LayoutBuilder(
            builder: (context, constraints) {
              return Stack(
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 800),
                    curve: Curves.easeOutCubic,
                    width: constraints.maxWidth * confidence,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [accentColor, accentColor.withOpacity(0.7)],
                      ),
                      borderRadius: BorderRadius.circular(5),
                      boxShadow: [
                        BoxShadow(
                          color: accentColor.withOpacity(0.5),
                          blurRadius: 8,
                        ),
                      ],
                    ),
                  ),
                ],
              );
            },
          ),
        ),
        const SizedBox(height: 8),
        // Confidence level indicator
        Row(
          children: [
            Icon(
              _getConfidenceIcon(),
              size: 16,
              color: _getConfidenceColor(),
            ),
            const SizedBox(width: 6),
            Text(
              _getConfidenceText(),
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: _getConfidenceColor(),
              ),
            ),
          ],
        ),
      ],
    );
  }
  
  Widget _buildTopPredictions(Color accentColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Other Possibilities',
          style: TextStyle(
            fontSize: 14,
            color: Colors.white.withOpacity(0.7),
          ),
        ),
        const SizedBox(height: 12),
        ...result.topPredictions.skip(1).take(2).map((prediction) {
          final percentage = (prediction.value * 100).toStringAsFixed(1);
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              children: [
                Container(
                  width: 6,
                  height: 6,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    prediction.key,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(0.6),
                    ),
                  ),
                ),
                Text(
                  '$percentage%',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.white.withOpacity(0.5),
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
  
  IconData _getConfidenceIcon() {
    if (result.confidence >= 0.8) return Icons.verified_rounded;
    if (result.confidence >= 0.6) return Icons.thumb_up_rounded;
    return Icons.help_outline_rounded;
  }
  
  Color _getConfidenceColor() {
    if (result.confidence >= 0.8) return const Color(0xFF2ECC71);
    if (result.confidence >= 0.6) return const Color(0xFFF39C12);
    return const Color(0xFFE74C3C);
  }
  
  String _getConfidenceText() {
    if (result.confidence >= 0.8) return 'High confidence - Reliable result';
    if (result.confidence >= 0.6) return 'Medium confidence';
    return 'Low confidence - Verify manually';
  }
}
