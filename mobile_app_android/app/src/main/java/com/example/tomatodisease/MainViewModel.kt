package com.example.tomatodisease

import android.content.Context
import android.graphics.Bitmap
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

/**
 * Simple MVVM ViewModel that delegates classification to ImageClassifier.
 */
class MainViewModel : ViewModel() {
    private val _prediction = MutableLiveData<Prediction>()
    val prediction: LiveData<Prediction> = _prediction

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    var lastImageUri: android.net.Uri? = null

    private var classifier: ImageClassifier? = null

    fun ensureClassifier(context: Context) {
        if (classifier == null) {
            classifier = ImageClassifier.create(context)
        }
    }

    fun classifyBitmap(bitmap: Bitmap, context: Context) {
        ensureClassifier(context)
        try {
            val result = classifier!!.classify(bitmap)
            _prediction.postValue(result)
        } catch (e: Exception) {
            _error.postValue(e.message)
        }
    }
}

data class Prediction(val label: String, val confidence: Float)
