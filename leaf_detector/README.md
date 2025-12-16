# Leaf detector training

This folder contains a small script to train a binary `leaf` / `nonleaf` classifier used to screen uploads before the main disease model runs.

Prepare data structure:

```
leaf_detector_data/
  train/
    leaf/
    nonleaf/
  val/
    leaf/
    nonleaf/
```

Then run:

```bash
python train_detector.py
```

The trained model will be saved to `models/leaf_detector.h5` by default. You can change the output path via `LEAF_DETECTOR_OUT` env var.
