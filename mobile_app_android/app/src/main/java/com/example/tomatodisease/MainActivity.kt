package com.example.tomatodisease

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.ProgressBar
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Home screen: Camera and Gallery buttons, shows loading and navigates to ResultActivity.
 */
class MainActivity : AppCompatActivity() {
    private val viewModel: MainViewModel by viewModels()

    private lateinit var btnCamera: Button
    private lateinit var btnGallery: Button
    private lateinit var preview: ImageView
    private lateinit var loading: ProgressBar

    private val cameraLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            val bitmap = result.data?.extras?.get("data") as? Bitmap
            bitmap?.let { handleBitmap(it) }
        }
    }

    private val galleryLauncher = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { handleUri(it) }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        btnCamera = findViewById(R.id.btnCamera)
        btnGallery = findViewById(R.id.btnGallery)
        preview = findViewById(R.id.previewImage)
        loading = findViewById(R.id.loading)

        btnCamera.setOnClickListener { openCamera() }
        btnGallery.setOnClickListener { openGallery() }

        viewModel.prediction.observe(this) { prediction ->
            // Navigate to result with extras
            loading.visibility = View.GONE
            val intent = Intent(this, ResultActivity::class.java).apply {
                putExtra("label", prediction.label)
                putExtra("confidence", prediction.confidence)
                putExtra("imageUri", viewModel.lastImageUri?.toString())
            }
            startActivity(intent)
        }

        viewModel.error.observe(this) { err ->
            loading.visibility = View.GONE
            if (!err.isNullOrEmpty()) {
                // Simple error handling
                preview.setImageResource(R.drawable.ic_error)
            }
        }
    }

    private fun openCamera() {
        if (checkAndRequestPermissions()) {
            val takePicture = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
            cameraLauncher.launch(takePicture)
        }
    }

    private fun openGallery() {
        if (checkAndRequestPermissions()) {
            galleryLauncher.launch("image/*")
        }
    }

    private fun handleUri(uri: Uri) {
        lifecycleScope.launch(Dispatchers.IO) {
            val bitmap = MediaStore.Images.Media.getBitmap(contentResolver, uri)
            viewModel.lastImageUri = uri
            runOnUiThread { preview.setImageBitmap(bitmap); loading.visibility = View.VISIBLE }
            viewModel.classifyBitmap(bitmap, this@MainActivity)
        }
    }

    private fun handleBitmap(bitmap: Bitmap) {
        lifecycleScope.launch(Dispatchers.IO) {
            viewModel.lastImageUri = null
            runOnUiThread { preview.setImageBitmap(bitmap); loading.visibility = View.VISIBLE }
            viewModel.classifyBitmap(bitmap, this@MainActivity)
        }
    }

    private fun checkAndRequestPermissions(): Boolean {
        val needed = mutableListOf<String>()
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.CAMERA)
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.READ_EXTERNAL_STORAGE)
        }
        return if (needed.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, needed.toTypedArray(), 1001)
            false
        } else true
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        // If granted, do nothing; user can tap again
    }
}
