# 📚 SNOUTIQ Dataset Directory

## Required Dataset Files

Place your 11 JSON dataset files in this directory. The system expects files with names starting with `master_` and ending with `_dataset.json`.

### Required Files:

1. `master_emergency_dataset.json`
2. `master_digestive_dataset.json`
3. `master_respiratory_dataset.json`
4. `master_urinary_dataset.json`
5. `master_joint_mobility_dataset.json`
6. `master_reproductive_dataset.json`
7. `master_skin_coat_dataset.json`
8. `master_eyes_ears_dataset.json`
9. `master_behavioral_dataset.json`
10. `master_nutrition_weight_dataset.json`
11. Any additional dataset files

## Dataset Format

Each JSON file should follow this structure:

```json
{
  "entries": [
    {
      "symptom": "Symptom name",
      "description": "Detailed description",
      "severity": "emergency/urgent/routine",
      "species": "dogs/cats/both",
      "home_care_india": "Home care instructions specific to India",
      "vet_triggers": "When to see a veterinarian",
      "service_recommendation": "in_clinic/video_consult",
      "indian_climate_factors": "Climate-specific considerations (optional)"
    }
  ]
}
```

## Verification

After adding your dataset files, you can verify they're loaded correctly:

1. Start the backend server: `python app.py`
2. Check the console output for dataset loading confirmation
3. Visit: `http://localhost:5000/datasets/info`

The system will automatically load all files matching `master_*_dataset.json` pattern.

## Notes

- Files are loaded at server startup
- Minimum 1 dataset file required
- Total entries across all datasets will be displayed on startup
- Invalid JSON files will be skipped with a warning

**Status**: ⚠️ **ADD YOUR DATASET FILES HERE**
