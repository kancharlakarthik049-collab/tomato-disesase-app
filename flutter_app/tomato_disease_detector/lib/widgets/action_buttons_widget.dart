/// Action Buttons Widget - Professional Dark Theme
/// 
/// Modern camera and gallery selection buttons with gradients

import 'package:flutter/material.dart';

class ActionButtonsWidget extends StatelessWidget {
  final VoidCallback onCameraPressed;
  final VoidCallback onGalleryPressed;
  final bool isEnabled;
  
  const ActionButtonsWidget({
    super.key,
    required this.onCameraPressed,
    required this.onGalleryPressed,
    this.isEnabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Camera button - Primary action (filled)
        Expanded(
          child: _buildGradientButton(
            onPressed: isEnabled ? onCameraPressed : null,
            icon: Icons.camera_alt_rounded,
            label: 'Take Photo',
            isPrimary: true,
          ),
        ),
        const SizedBox(width: 16),
        // Gallery button - Secondary action (outlined)
        Expanded(
          child: _buildGradientButton(
            onPressed: isEnabled ? onGalleryPressed : null,
            icon: Icons.photo_library_rounded,
            label: 'Gallery',
            isPrimary: false,
          ),
        ),
      ],
    );
  }
  
  Widget _buildGradientButton({
    required VoidCallback? onPressed,
    required IconData icon,
    required String label,
    required bool isPrimary,
  }) {
    final isDisabled = onPressed == null;
    
    if (isPrimary) {
      return Container(
        decoration: BoxDecoration(
          gradient: isDisabled
              ? LinearGradient(
                  colors: [Colors.grey.shade600, Colors.grey.shade700],
                )
              : const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFF2ECC71), Color(0xFF27AE60)],
                ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: isDisabled
              ? []
              : [
                  BoxShadow(
                    color: const Color(0xFF2ECC71).withOpacity(0.4),
                    blurRadius: 15,
                    offset: const Offset(0, 8),
                  ),
                ],
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onPressed,
            borderRadius: BorderRadius.circular(16),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 18),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    icon,
                    color: Colors.white,
                    size: 22,
                  ),
                  const SizedBox(width: 10),
                  Text(
                    label,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    } else {
      return Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isDisabled
                ? Colors.grey.shade600
                : const Color(0xFF2ECC71),
            width: 2,
          ),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white.withOpacity(0.05),
              Colors.white.withOpacity(0.02),
            ],
          ),
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onPressed,
            borderRadius: BorderRadius.circular(14),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 18),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    icon,
                    color: isDisabled
                        ? Colors.grey.shade600
                        : const Color(0xFF2ECC71),
                    size: 22,
                  ),
                  const SizedBox(width: 10),
                  Text(
                    label,
                    style: TextStyle(
                      color: isDisabled
                          ? Colors.grey.shade600
                          : const Color(0xFF2ECC71),
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }
  }
}
