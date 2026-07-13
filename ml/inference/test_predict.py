from ml.inference.predict import predict_risk
indicators = [
    {
        "source": "manifest",
        "description": "SEND_SMS",
        "severity": "high"
    },
    {
        "source": "manifest",
        "description": "READ_SMS",
        "severity": "high"
    },
    {
        "source": "yara",
        "description": "Spyware Signature",
        "severity": "critical"
    }
]

print(predict_risk(indicators))