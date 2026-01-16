package com.example.tomatodisease

/**
 * Small repository holding descriptions and treatments for diseases.
 * In production this should be externalized to JSON or DB.
 */
object DiseaseRepository {
    private val info = mapOf(
        "Tomato___Bacterial_spot" to "Bacterial spot: small dark spots; remove affected leaves and apply copper-based bactericide.",
        "Tomato___Early_blight" to "Early blight: brown lesions and concentric rings; practice crop rotation and fungicide spray.",
        "Tomato___Late_blight" to "Late blight: water-soaked lesions; remove infected plants, use appropriate fungicides.",
        "Tomato___Leaf_Mold" to "Leaf mold: yellowing and mold under leaves; increase ventilation and use fungicide.",
        "Tomato___Septoria_leaf_spot" to "Septoria leaf spot: small dark spots; remove debris and apply fungicide.",
        "Tomato___Spider_mites" to "Spider mites: tiny spots and webbing; use miticides and encourage predators.",
        "Tomato___Target_Spot" to "Target spot: target-shaped lesions; use disease-free seeds and fungicides.",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus" to "TYLCV: leaf curling and yellowing; control whitefly vector and use resistant varieties.",
        "Tomato___Tomato_mosaic_virus" to "TMV: mottling and stunted growth; remove infected plants and sanitize tools.",
        "Tomato___healthy" to "Healthy: no disease detected. Maintain good cultural practices."
    )

    fun getDescription(label: String): String {
        return info[label] ?: "No description available."
    }
}
