package com.example.tomatodisease

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

/**
 * Simple splash that navigates to MainActivity after a short delay.
 */
class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Minimal UI; could inflate a layout
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}
