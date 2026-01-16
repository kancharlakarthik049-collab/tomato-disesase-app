package com.example.tomatodisease

import android.net.Uri
import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide

class ResultActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_result)

        val imageView: ImageView = findViewById(R.id.resultImage)
        val labelView: TextView = findViewById(R.id.resultLabel)
        val confView: TextView = findViewById(R.id.resultConfidence)
        val descView: TextView = findViewById(R.id.resultDescription)

        val label = intent.getStringExtra("label") ?: "Unknown"
        val conf = intent.getFloatExtra("confidence", 0f)
        val uriString = intent.getStringExtra("imageUri")

        labelView.text = label
        confView.text = String.format("Confidence: %.2f%%", conf * 100)

        // Simple descriptions; in production, load from JSON or DB
        descView.text = DiseaseRepository.getDescription(label)

        if (uriString != null) {
            Glide.with(this).load(Uri.parse(uriString)).into(imageView)
        } else {
            // If image not from gallery, show placeholder
            imageView.setImageResource(R.drawable.ic_image)
        }
    }
}
