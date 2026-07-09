import zipfile
from xml.etree import ElementTree

import pytest

from core.static_analysis.apk_analyzer import APKAnalyzer


class FakeAPK:
    def get_package(self):
        return "com.example.spy"

    def get_androidversion_name(self):
        return "1.0"

    def get_androidversion_code(self):
        return "7"

    def get_permissions(self):
        return ["android.permission.INTERNET", "android.permission.RECEIVE_SMS"]

    def get_activities(self):
        return ["com.example.spy.MainActivity"]

    def get_services(self):
        return ["com.example.spy.SyncService"]

    def get_receivers(self):
        return ["com.example.spy.BootReceiver"]

    def get_providers(self):
        return ["com.example.spy.DataProvider"]

    def get_android_manifest_xml(self):
        manifest = """
        <manifest xmlns:android="http://schemas.android.com/apk/res/android">
            <application>
                <activity
                    android:name="com.example.spy.MainActivity"
                    android:exported="true" />
                <service
                    android:name="com.example.spy.SyncService"
                    android:exported="false" />
                <receiver
                    android:name="com.example.spy.BootReceiver"
                    android:exported="true" />
                <provider
                    android:name="com.example.spy.DataProvider"
                    android:exported="false" />
            </application>
        </manifest>
        """
        return ElementTree.fromstring(manifest)


def test_apk_analyzer_extracts_static_metadata(tmp_path, monkeypatch):
    apk_path = tmp_path / "sample.apk"
    with zipfile.ZipFile(apk_path, "w") as apk_zip:
        apk_zip.writestr("assets/config.txt", "callback=https://example.com/collect")

    monkeypatch.setattr(APKAnalyzer, "_load_apk", lambda self, path: FakeAPK())

    result = APKAnalyzer().analyze(str(apk_path))

    assert result["status"] == "analyzed"
    assert result["package_name"] == "com.example.spy"
    assert result["version"] == {"name": "1.0", "code": "7"}
    assert result["permissions"] == [
        "android.permission.INTERNET",
        "android.permission.RECEIVE_SMS",
    ]
    assert result["activities"] == ["com.example.spy.MainActivity"]
    assert result["services"] == ["com.example.spy.SyncService"]
    assert result["receivers"] == ["com.example.spy.BootReceiver"]
    assert result["providers"] == ["com.example.spy.DataProvider"]
    assert result["exported_components"] == [
        {"type": "activities", "name": "com.example.spy.MainActivity"},
        {"type": "receivers", "name": "com.example.spy.BootReceiver"},
    ]
    assert result["embedded_urls"] == ["https://example.com/collect"]


def test_apk_analyzer_raises_for_missing_apk():
    with pytest.raises(FileNotFoundError):
        APKAnalyzer().analyze("missing.apk")


def test_apk_analyzer_raises_for_invalid_scan_path(tmp_path):
    with pytest.raises(ValueError):
        APKAnalyzer().analyze(str(tmp_path))
