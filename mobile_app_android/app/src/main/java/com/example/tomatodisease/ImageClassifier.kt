package com.example.tomatodisease

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.Interpreter
import java.io.BufferedReader
import java.io.InputStreamReader
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import kotlin.math.max

/**
 * Lightweight image classifier using TensorFlow Lite Interpreter.
 * Expects Inception V3 converted to TFLite with input shape [1,299,299,3] and float32.
 */
class ImageClassifier private constructor(private val tflite: Interpreter, private val labels: List<String>) {
    companion object {
        private const val MODEL_NAME = "inception_v3_299.tflite"
        private const val INPUT_SIZE = 299
        private const val NUM_CHANNELS = 3
        private const val BYTES_PER_CHANNEL = 4 // float32

        fun create(context: Context): ImageClassifier {
            val assetFd = context.assets.openFd(MODEL_NAME)
            val input = assetFd.createInputStream()
            val fileChannel = input.channel
            val startOffset = assetFd.startOffset
            val declaredLength = assetFd.length
            val mapped: MappedByteBuffer = fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength)
            val tflite = Interpreter(mapped)
            val labels = loadLabels(context)
            return ImageClassifier(tflite, labels)
        }

        private fun loadLabels(context: Context): List<String> {
            val list = mutableListOf<String>()
            val reader = BufferedReader(InputStreamReader(context.assets.open("labels.txt")))
            reader.useLines { lines -> lines.forEach { list.add(it.trim()) } }
            return list
        }
    }

    fun classify(bitmap: Bitmap): Prediction {
        // Preprocess bitmap to 299x299 float32 ByteBuffer
        val resized = Bitmap.createScaledBitmap(bitmap, INPUT_SIZE, INPUT_SIZE, true)
        val byteBuffer = convertBitmapToByteBuffer(resized)

        // Output container: assume model outputs [1,labelCount]
        val output = Array(1) { FloatArray(labels.size) }

        tflite.run(byteBuffer, output)

        val confidences = output[0]
        var maxIdx = 0
        var maxConf = 0f
        for (i in confidences.indices) {
            if (confidences[i] > maxConf) {
                maxConf = confidences[i]
                maxIdx = i
            }
        }

        val label = if (maxIdx < labels.size) labels[maxIdx] else "Unknown"
        return Prediction(label, maxConf)
    }

    private fun convertBitmapToByteBuffer(bitmap: Bitmap): ByteBuffer {
        val byteBuffer = ByteBuffer.allocateDirect(INPUT_SIZE * INPUT_SIZE * NUM_CHANNELS * BYTES_PER_CHANNEL)
        byteBuffer.order(ByteOrder.nativeOrder())
        val intValues = IntArray(INPUT_SIZE * INPUT_SIZE)
        bitmap.getPixels(intValues, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)
        var pixelIndex = 0
        for (i in 0 until INPUT_SIZE) {
            for (j in 0 until INPUT_SIZE) {
                val `val` = intValues[pixelIndex++] // ARGB
                // Extract RGB and normalize to [-1,1] for Inception V3
                val r = ((`val` shr 16) and 0xFF)
                val g = ((`val` shr 8) and 0xFF)
                val b = (`val` and 0xFF)
                // Normalize to [-1,1]
                byteBuffer.putFloat((r / 127.5f) - 1f)
                byteBuffer.putFloat((g / 127.5f) - 1f)
                byteBuffer.putFloat((b / 127.5f) - 1f)
            }
        }
        return byteBuffer
    }
}
