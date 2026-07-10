"""
TEMPORARY: quick manual check that predict_risk() works end-to-end,
using a fake (but realistically shaped) static analysis result instead
of a real APK, since we don't have one handy on this branch.

Not a real pytest test — just a manual sanity check. Delete once the
real integration test suite covers this.
"""

from ml.predict_risk import predict_risk

# Simulates a SUSPICIOUS file's static analysis result — a realistic
# combined permission set, matching patterns real spyware tends to request
suspicious_result = {
    "file": "fake_spyware.apk",
    "file_type": "apk",
    "hash_matcher": {"status": "malicious", "sha256": "abc123", "family": "TestSpy", "source": "test"},
    "yara": {"status": "matched", "match_count": 2, "matches": []},
    "analysis": {
        "status": "analyzed",
        "permissions": [
            "android.permission.READ_SMS",
            "android.permission.SEND_SMS",
            "android.permission.RECEIVE_SMS",
            "android.permission.READ_PHONE_STATE",
            "android.permission.GET_ACCOUNTS",
            "android.permission.RECORD_AUDIO",
            "android.permission.CAMERA",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.WAKE_LOCK",
            "android.permission.READ_CALL_LOG",
        ],
        "exported_components": [{"type": "activities", "name": "com.fake.Hidden"}],
        "embedded_urls": ["http://suspicious-server.example.com"],
    },
}

# Simulates a CLEAN, benign file's static analysis result
clean_result = {
    "file": "battery_saver.apk",
    "file_type": "apk",
    "hash_matcher": {"status": "clean", "sha256": "def456", "family": None, "source": None},
    "yara": {"status": "clean", "match_count": 0, "matches": []},
    "analysis": {
        "status": "analyzed",
        "permissions": [],
        "exported_components": [],
        "embedded_urls": [],
    },
}

print("Suspicious file risk score:", predict_risk(suspicious_result))
print("Clean file risk score:     ", predict_risk(clean_result))