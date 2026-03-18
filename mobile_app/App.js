import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  Button,
  Image,
  ActivityIndicator,
  ScrollView,
  Alert,
  TouchableOpacity,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

// Update this to your Render deployment URL
const BACKEND_URL = 'https://tomato-disease-app.onrender.com';

export default function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [maskUrl, setMaskUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [allPredictions, setAllPredictions] = useState(null);

  // Disease info for recommendations
  const diseaseInfo = {
    'Healthy': 'No disease detected. Maintain regular plant care.',
    'Bacterial_spot': 'Bacterial spot detected. Use copper-based fungicides and remove infected leaves.',
    'Early_blight': 'Early blight detected. Improve air circulation and apply fungicides.',
    'Late_blight': 'Late blight detected. This is serious. Use systemic fungicides and isolate plant.',
    'Leaf_Mold': 'Leaf mold detected. Reduce humidity and increase ventilation.',
    'Septoria_leaf_spot': 'Septoria leaf spot detected. Remove infected leaves and apply fungicides.',
    'Spider_mites': 'Spider mites detected. Use miticides or neem oil spray.',
    'Target_Spot': 'Target spot detected. Apply copper or sulfur-based fungicides.',
    'Yellow_Leaf_Curl_Virus': 'Yellow leaf curl virus detected. Remove infected plant and control whiteflies.',
    'Mosaic_virus': 'Mosaic virus detected. Remove plant to prevent spread. Control aphids.',
    'Uncertain': 'Uncertain prediction. Please provide a clearer image of the leaf.',
  };

  async function pickImage() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission required', 'Camera roll permission is required.');
      return;
    }

    const picker = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });

    // Check for canceled property (fixed API)
    if (!picker.canceled) {
      setImage(picker.assets[0].uri);
      setResult(null);
      setMaskUrl(null);
      setAllPredictions(null);
    }
  }

  async function takePhoto() {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission required', 'Camera permission is required.');
      return;
    }

    const photo = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });

    if (!photo.canceled) {
      setImage(photo.assets[0].uri);
      setResult(null);
      setMaskUrl(null);
      setAllPredictions(null);
    }
  }

  async function uploadImage() {
    if (!image) {
      Alert.alert('No image', 'Please select or take a photo first.');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      
      // Extract filename from URI
      const filename = image.split('/').pop() || 'image.jpg';
      
      // Add file to form data
      formData.append('file', {
        uri: image,
        name: filename,
        type: 'image/jpeg',
      });

      const response = await fetch(`${BACKEND_URL}/api/predict`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      
      setResult(data);
      setAllPredictions(data.all_predictions);
      
      if (data.mask) {
        setMaskUrl(`data:image/png;base64,${data.mask}`);
      }

      Alert.alert('Success', `Prediction: ${data.prediction}\nConfidence: ${(data.confidence * 100).toFixed(2)}%`);
    } catch (error) {
      console.error('Upload error:', error);
      Alert.alert('Error', `Failed to upload image: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🍅 Tomato Disease Identifier</Text>
        <Text style={styles.subtitle}>AI-powered disease detection for healthy crops</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Select Image</Text>
        
        <TouchableOpacity
          style={styles.buttonPrimary}
          onPress={pickImage}
        >
          <Text style={styles.buttonText}>📷 Choose from Gallery</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.buttonSecondary}
          onPress={takePhoto}
        >
          <Text style={styles.buttonText}>📸 Take a Photo</Text>
        </TouchableOpacity>
      </View>

      {image && (
        <View style={styles.imageContainer}>
          <Text style={styles.sectionTitle}>Selected Image</Text>
          <Image source={{ uri: image }} style={styles.image} />
        </View>
      )}

      {image && !loading && (
        <TouchableOpacity
          style={styles.analyzeButton}
          onPress={uploadImage}
        >
          <Text style={styles.buttonText}>🔍 Analyze Image</Text>
        </TouchableOpacity>
      )}

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#2ecc71" />
          <Text style={styles.loadingText}>Analyzing image...</Text>
        </View>
      )}

      {result && (
        <View style={styles.resultContainer}>
          <Text style={styles.sectionTitle}>Diagnosis</Text>
          
          <View style={styles.predictionBox}>
            <Text style={styles.predictionLabel}>Detected Disease:</Text>
            <Text style={[styles.predictionValue, { color: result.prediction === 'Healthy' ? '#2ecc71' : '#e74c3c' }]}>
              {result.prediction}
            </Text>
            <Text style={styles.confidenceText}>
              Confidence: {(result.confidence * 100).toFixed(2)}%
            </Text>
          </View>

          <View style={styles.recommendationBox}>
            <Text style={styles.recommendationLabel}>Recommendation:</Text>
            <Text style={styles.recommendationText}>
              {diseaseInfo[result.prediction] || 'Please provide more information.'}
            </Text>
          </View>

          {maskUrl && (
            <View style={styles.maskContainer}>
              <Text style={styles.sectionTitle}>Green Leaf Detection</Text>
              <Image source={{ uri: maskUrl }} style={styles.maskImage} />
              <Text style={styles.maskCaption}>
                Green areas show detected leaf regions
              </Text>
            </View>
          )}

          {allPredictions && (
            <View style={styles.allPredictionsContainer}>
              <Text style={styles.sectionTitle}>All Predictions</Text>
              {Object.entries(allPredictions).map(([disease, confidence]) => (
                <View key={disease} style={styles.predictionRow}>
                  <Text style={styles.diseaseName}>{disease}</Text>
                  <Text style={styles.confidenceScore}>
                    {(confidence * 100).toFixed(2)}%
                  </Text>
                </View>
              ))}
            </View>
          )}

          <TouchableOpacity
            style={styles.resetButton}
            onPress={() => {
              setImage(null);
              setResult(null);
              setMaskUrl(null);
              setAllPredictions(null);
            }}
          >
            <Text style={styles.buttonText}>↻ Analyze Another Image</Text>
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.footer}>
        <Text style={styles.footerText}>v1.0.0</Text>
        <Text style={styles.footerText}>Backend: {BACKEND_URL}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    backgroundColor: '#27ae60',
    padding: 20,
    paddingTop: 40,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: '#ecf0f1',
  },
  section: {
    padding: 16,
    backgroundColor: '#fff',
    marginHorizontal: 12,
    marginVertical: 12,
    borderRadius: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: 12,
  },
  buttonPrimary: {
    backgroundColor: '#3498db',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  buttonSecondary: {
    backgroundColor: '#9b59b6',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  analyzeButton: {
    backgroundColor: '#2ecc71',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 12,
    marginVertical: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  imageContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 12,
    marginVertical: 12,
    borderRadius: 8,
    padding: 12,
  },
  image: {
    width: '100%',
    height: 300,
    borderRadius: 8,
  },
  loadingContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 12,
    marginVertical: 12,
    borderRadius: 8,
    padding: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#7f8c8d',
  },
  resultContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 12,
    marginVertical: 12,
    borderRadius: 8,
    padding: 16,
  },
  predictionBox: {
    backgroundColor: '#ecf0f1',
    padding: 14,
    borderRadius: 6,
    marginBottom: 12,
  },
  predictionLabel: {
    fontSize: 13,
    color: '#7f8c8d',
    marginBottom: 6,
  },
  predictionValue: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 6,
  },
  confidenceText: {
    fontSize: 13,
    color: '#34495e',
    fontWeight: '500',
  },
  recommendationBox: {
    backgroundColor: '#fef5e7',
    padding: 12,
    borderRadius: 6,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#f39c12',
  },
  recommendationLabel: {
    fontSize: 12,
    color: '#d68910',
    fontWeight: '600',
    marginBottom: 6,
  },
  recommendationText: {
    fontSize: 13,
    color: '#7d6608',
    lineHeight: 20,
  },
  maskContainer: {
    marginTop: 12,
  },
  maskImage: {
    width: '100%',
    height: 250,
    borderRadius: 8,
    marginVertical: 10,
  },
  maskCaption: {
    fontSize: 12,
    color: '#7f8c8d',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  allPredictionsContainer: {
    backgroundColor: '#ecf0f1',
    padding: 12,
    borderRadius: 6,
    marginTop: 12,
  },
  predictionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#bdc3c7',
  },
  diseaseName: {
    fontSize: 12,
    color: '#2c3e50',
    fontWeight: '500',
  },
  confidenceScore: {
    fontSize: 12,
    color: '#27ae60',
    fontWeight: '600',
  },
  resetButton: {
    backgroundColor: '#e74c3c',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 12,
  },
  footer: {
    padding: 20,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#ecf0f1',
    marginTop: 20,
  },
  footerText: {
    fontSize: 12,
    color: '#95a5a6',
    marginVertical: 2,
  },
});
