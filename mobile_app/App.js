import React, { useState } from 'react';
import { StyleSheet, View, Button, Image, Text, ActivityIndicator, Alert, ScrollView } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

// IMPORTANT: update this to your backend address (include port), e.g. http://192.168.1.10:5000
const BACKEND_URL = 'http://YOUR_BACKEND_HOST:5000';

export default function App() {
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [maskUrl, setMaskUrl] = useState(null);

  async function pickImage() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission required', 'Camera roll permission is required to pick images.');
      return;
    }

    const picker = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });

    if (!picker.cancelled) {
      setImage(picker.uri);
      setResult(null);
      setMaskUrl(null);
    }
  }

  async function takePhoto() {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) {
      Alert.alert('Permission required', 'Camera permission is required to take photos.');
      return;
    }

    const picker = await ImagePicker.launchCameraAsync({
      quality: 0.8,
    });

    if (!picker.cancelled) {
      setImage(picker.uri);
      setResult(null);
      setMaskUrl(null);
    }
  }

  async function uploadImage() {
    if (!image) return;
    setLoading(true);
    setResult(null);
    setMaskUrl(null);
    try {
      const form = new FormData();
      const filename = image.split('/').pop();
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : `image`;

      form.append('file', {
        uri: image,
        name: filename,
        type,
      });

      const res = await fetch(`${BACKEND_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
        body: form,
      });

      const data = await res.json();
      if (!res.ok) {
        Alert.alert('Error', data.error || 'Prediction failed');
      } else {
        setResult(data);
        if (data.mask) {
          setMaskUrl(`${BACKEND_URL}/static/uploads/${data.mask}`);
        }
      }
    } catch (e) {
      Alert.alert('Error', String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Tomato Disease Detector</Text>
      <View style={{ flexDirection: 'row', gap: 8 }}>
        <Button title="Pick Image" onPress={pickImage} />
        <View style={{ width: 12 }} />
        <Button title="Take Photo" onPress={takePhoto} />
      </View>

      {image && <Image source={{ uri: image }} style={styles.image} />}
      <View style={{ height: 12 }} />
      <Button title="Upload and Predict" onPress={uploadImage} disabled={!image || loading} />
      {loading && <ActivityIndicator style={{ marginTop: 12 }} />}

      {result && (
        <View style={{ marginTop: 12, alignItems: 'center' }}>
          <Text style={styles.pred}>Prediction: {result.prediction}</Text>
          <Text style={styles.pred}>Confidence: {result.confidence}%</Text>
        </View>
      )}

      {maskUrl && (
        <View style={{ marginTop: 16, alignItems: 'center' }}>
          <Text style={{ fontSize: 16, marginBottom: 8 }}>Detected Green Mask</Text>
          <Image source={{ uri: maskUrl }} style={{ width: 250, height: 250 }} />
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, alignItems: 'center', justifyContent: 'center', padding: 20 },
  title: { fontSize: 20, marginBottom: 12 },
  image: { width: 250, height: 250, resizeMode: 'cover', marginTop: 12 },
  pred: { fontSize: 16, marginTop: 6 }
});
