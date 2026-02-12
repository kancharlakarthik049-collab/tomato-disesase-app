/// Image Preview Widget - Professional Dark Theme
/// 
/// Displays the selected image with modern styling and loading effects

import 'dart:io';
import 'dart:ui';
import 'package:flutter/material.dart';

class ImagePreviewWidget extends StatelessWidget {
  final File? imageFile;
  final bool isLoading;
  
  const ImagePreviewWidget({
    super.key,
    this.imageFile,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 320,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withOpacity(0.1),
            Colors.white.withOpacity(0.05),
          ],
        ),
        border: Border.all(
          color: Colors.white.withOpacity(0.2),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // Background gradient
          Container(
            decoration: BoxDecoration(
              gradient: RadialGradient(
                center: Alignment.center,
                radius: 1.5,
                colors: [
                  const Color(0xFF16213E),
                  const Color(0xFF1A1A2E),
                ],
              ),
            ),
          ),
          
          // Image or placeholder
          if (imageFile != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(22),
              child: Image.file(
                imageFile!,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return _buildPlaceholder(context);
                },
              ),
            )
          else
            _buildPlaceholder(context),
          
          // Corner decorations
          if (imageFile == null) ...[
            Positioned(
              top: 16,
              left: 16,
              child: _buildCornerDecoration(),
            ),
            Positioned(
              top: 16,
              right: 16,
              child: Transform.rotate(
                angle: 1.5708, // 90 degrees
                child: _buildCornerDecoration(),
              ),
            ),
            Positioned(
              bottom: 16,
              left: 16,
              child: Transform.rotate(
                angle: -1.5708,
                child: _buildCornerDecoration(),
              ),
            ),
            Positioned(
              bottom: 16,
              right: 16,
              child: Transform.rotate(
                angle: 3.1416, // 180 degrees
                child: _buildCornerDecoration(),
              ),
            ),
          ],
          
          // Loading overlay
          if (isLoading)
            ClipRRect(
              borderRadius: BorderRadius.circular(22),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 5, sigmaY: 5),
                child: Container(
                  color: Colors.black.withOpacity(0.6),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // Animated scanning effect
                        Stack(
                          alignment: Alignment.center,
                          children: [
                            SizedBox(
                              width: 80,
                              height: 80,
                              child: CircularProgressIndicator(
                                strokeWidth: 3,
                                valueColor: const AlwaysStoppedAnimation<Color>(
                                  Color(0xFF2ECC71),
                                ),
                              ),
                            ),
                            Container(
                              width: 50,
                              height: 50,
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(
                                  colors: [Color(0xFF2ECC71), Color(0xFF27AE60)],
                                ),
                                borderRadius: BorderRadius.circular(15),
                              ),
                              child: const Icon(
                                Icons.psychology,
                                color: Colors.white,
                                size: 28,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        const Text(
                          'Analyzing Leaf...',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            letterSpacing: 0.5,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'AI is detecting diseases',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.7),
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
  
  Widget _buildCornerDecoration() {
    return Container(
      width: 30,
      height: 30,
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: const Color(0xFF2ECC71).withOpacity(0.5),
            width: 3,
          ),
          left: BorderSide(
            color: const Color(0xFF2ECC71).withOpacity(0.5),
            width: 3,
          ),
        ),
      ),
    );
  }
  
  Widget _buildPlaceholder(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  const Color(0xFF2ECC71).withOpacity(0.2),
                  const Color(0xFF27AE60).withOpacity(0.1),
                ],
              ),
              borderRadius: BorderRadius.circular(24),
            ),
            child: Icon(
              Icons.add_photo_alternate_rounded,
              size: 60,
              color: const Color(0xFF2ECC71).withOpacity(0.8),
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'No Image Selected',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Take a photo or choose from gallery',
            style: TextStyle(
              fontSize: 14,
              color: Colors.white.withOpacity(0.5),
            ),
          ),
        ],
      ),
    );
  }
}
