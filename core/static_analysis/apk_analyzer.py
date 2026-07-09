import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


ANDROID_NAMESPACE = "{http://schemas.android.com/apk/res/android}"
RULE_URL_PATTERN = re.compile(rb"https?://[^\s\"'<>\\)]+")


class APKAnalyzer:
    """Extract static metadata and indicators from Android APK files."""

    def analyze(self, file_path: str) -> dict:
        """
        Analyze an APK without executing it.

        Args:
            file_path: Path to the APK file.

        Returns:
            A structured dictionary containing manifest metadata, components,
            exported components, and embedded URLs.

        Raises:
            FileNotFoundError: If the APK path does not exist.
            ValueError: If the path is not a file or the APK cannot be parsed.
            RuntimeError: If androguard is not installed.
        """

        apk_path = self._validate_apk_path(file_path)
        apk = self._load_apk(apk_path)

        return {
            "status": "analyzed",
            "file_path": str(apk_path),
            "package_name": apk.get_package(),
            "version": {
                "name": apk.get_androidversion_name(),
                "code": apk.get_androidversion_code(),
            },
            "permissions": self._normalize_list(apk.get_permissions()),
            "activities": self._normalize_list(apk.get_activities()),
            "services": self._normalize_list(apk.get_services()),
            "receivers": self._normalize_list(apk.get_receivers()),
            "providers": self._normalize_list(apk.get_providers()),
            "exported_components": self._extract_exported_components(apk),
            "embedded_urls": self._extract_embedded_urls(apk_path),
        }

    def _validate_apk_path(self, file_path: str) -> Path:
        """
        Validate that the provided APK path exists and points to a file.

        Args:
            file_path: Path to validate.

        Returns:
            A resolved Path object for the APK.

        Raises:
            FileNotFoundError: If the path does not exist.
            ValueError: If the path is not a file.
        """

        apk_path = Path(file_path)

        if not apk_path.exists():
            raise FileNotFoundError(f"APK file does not exist: {apk_path}")

        if not apk_path.is_file():
            raise ValueError(f"APK path is not a file: {apk_path}")

        return apk_path

    def _load_apk(self, apk_path: Path):
        """
        Load an APK with androguard for static analysis.

        Args:
            apk_path: Path to the APK file.

        Returns:
            An androguard APK object.

        Raises:
            RuntimeError: If androguard is unavailable.
            ValueError: If androguard cannot parse the APK.
        """

        try:
            from androguard.core.apk import APK
        except ImportError as exc:
            raise RuntimeError("androguard is required for APK analysis") from exc

        try:
            return APK(str(apk_path))
        except Exception as exc:
            raise ValueError(f"Invalid APK file: {apk_path}") from exc

    def _extract_exported_components(self, apk) -> list:
        """
        Extract manifest components explicitly marked as exported.

        Args:
            apk: An androguard APK object.

        Returns:
            A list of dictionaries describing exported components.
        """

        manifest = apk.get_android_manifest_xml()
        if manifest is None:
            return []

        component_tags = {
            "activity": "activities",
            "service": "services",
            "receiver": "receivers",
            "provider": "providers",
        }
        exported_components = []

        for tag_name, component_type in component_tags.items():
            for element in manifest.iter(tag_name):
                exported = element.get(f"{ANDROID_NAMESPACE}exported")
                name = element.get(f"{ANDROID_NAMESPACE}name")

                if exported == "true" and name:
                    exported_components.append(
                        {
                            "type": component_type,
                            "name": name,
                        }
                    )

        return sorted(exported_components, key=lambda item: (item["type"], item["name"]))

    def _extract_embedded_urls(self, apk_path: Path) -> list:
        """
        Extract embedded HTTP and HTTPS URLs from APK file contents.

        Args:
            apk_path: Path to the APK file.

        Returns:
            A sorted list of unique URLs found in static APK contents.
        """

        urls = set()

        try:
            with zipfile.ZipFile(apk_path) as apk_zip:
                for member in apk_zip.infolist():
                    if member.is_dir():
                        continue

                    data = apk_zip.read(member)
                    urls.update(
                        match.decode("utf-8", errors="ignore")
                        for match in RULE_URL_PATTERN.findall(data)
                    )
        except zipfile.BadZipFile:
            return []

        return sorted(urls)

    def _normalize_list(self, values) -> list:
        """
        Convert androguard iterable results into sorted unique lists.

        Args:
            values: Iterable values returned by androguard.

        Returns:
            A sorted list of unique non-empty values.
        """

        if not values:
            return []

        return sorted({value for value in values if value})
