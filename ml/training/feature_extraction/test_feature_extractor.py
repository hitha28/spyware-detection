from feature_extractor import extract_static_features

# Sample indicators (like the ones module will return)
sample_indicators = [
    {
        "source": "apk",
        "description": "Requests risky permission: SEND_SMS",
        "severity": "high"
    },
    {
        "source": "apk",
        "description": "Requests risky permission: CAMERA",
        "severity": "medium"
    },
    {
        "source": "yara",
        "description": "Matched spyware rule",
        "severity": "critical"
    }
]

features = extract_static_features(sample_indicators)

print("Feature Vector:")
print(features)
