"""
Extracts a numeric feature vector from Shivanshi's static analysis output,
matching the 115 real permission-based features from the Drebin-215
dataset (see ml/training/datasets/real_drebin/).

Note: the original Drebin-215 dataset has 215 features total; the other
~100 are API-call/behavior signals that our static engine doesn't
currently extract, so this uses the permission-only subset.
"""

# The 115 permission names used in the real Drebin training dataset.
# Order matters — must exactly match FEATURE_NAMES used at training time.
FEATURE_NAMES = [
    'SEND_SMS', 'READ_PHONE_STATE', 'GET_ACCOUNTS', 'RECEIVE_SMS', 'READ_SMS',
    'USE_CREDENTIALS', 'MANAGE_ACCOUNTS', 'WRITE_SMS', 'READ_SYNC_SETTINGS',
    'AUTHENTICATE_ACCOUNTS', 'WRITE_HISTORY_BOOKMARKS', 'INSTALL_PACKAGES',
    'CAMERA', 'WRITE_SYNC_SETTINGS', 'READ_HISTORY_BOOKMARKS', 'INTERNET',
    'RECORD_AUDIO', 'NFC', 'ACCESS_LOCATION_EXTRA_COMMANDS', 'WRITE_APN_SETTINGS',
    'BIND_REMOTEVIEWS', 'READ_PROFILE', 'MODIFY_AUDIO_SETTINGS', 'READ_SYNC_STATS',
    'BROADCAST_STICKY', 'WAKE_LOCK', 'RECEIVE_BOOT_COMPLETED', 'RESTART_PACKAGES',
    'BLUETOOTH', 'READ_CALENDAR', 'READ_CALL_LOG', 'SUBSCRIBED_FEEDS_WRITE',
    'READ_EXTERNAL_STORAGE', 'VIBRATE', 'ACCESS_NETWORK_STATE',
    'SUBSCRIBED_FEEDS_READ', 'CHANGE_WIFI_MULTICAST_STATE', 'WRITE_CALENDAR',
    'MASTER_CLEAR', 'UPDATE_DEVICE_STATS', 'WRITE_CALL_LOG', 'DELETE_PACKAGES',
    'GET_TASKS', 'GLOBAL_SEARCH', 'DELETE_CACHE_FILES', 'WRITE_USER_DICTIONARY',
    'REORDER_TASKS', 'WRITE_PROFILE', 'SET_WALLPAPER', 'BIND_INPUT_METHOD',
    'READ_SOCIAL_STREAM', 'READ_USER_DICTIONARY', 'PROCESS_OUTGOING_CALLS',
    'CALL_PRIVILEGED', 'BIND_WALLPAPER', 'RECEIVE_WAP_PUSH', 'DUMP',
    'BATTERY_STATS', 'ACCESS_COARSE_LOCATION', 'SET_TIME', 'WRITE_SOCIAL_STREAM',
    'WRITE_SETTINGS', 'REBOOT', 'BLUETOOTH_ADMIN', 'BIND_DEVICE_ADMIN',
    'WRITE_GSERVICES', 'KILL_BACKGROUND_PROCESSES', 'SET_ALARM', 'ACCOUNT_MANAGER',
    'STATUS_BAR', 'PERSISTENT_ACTIVITY', 'CHANGE_NETWORK_STATE', 'RECEIVE_MMS',
    'SET_TIME_ZONE', 'CONTROL_LOCATION_UPDATES', 'BROADCAST_WAP_PUSH',
    'BIND_ACCESSIBILITY_SERVICE', 'ADD_VOICEMAIL', 'CALL_PHONE', 'BIND_APPWIDGET',
    'FLASHLIGHT', 'READ_LOGS', 'SET_PROCESS_LIMIT', 'MOUNT_UNMOUNT_FILESYSTEMS',
    'BIND_TEXT_SERVICE', 'INSTALL_LOCATION_PROVIDER', 'SYSTEM_ALERT_WINDOW',
    'MOUNT_FORMAT_FILESYSTEMS', 'CHANGE_CONFIGURATION', 'CLEAR_APP_USER_DATA',
    'CHANGE_WIFI_STATE', 'READ_FRAME_BUFFER', 'ACCESS_SURFACE_FLINGER',
    'BROADCAST_SMS', 'EXPAND_STATUS_BAR', 'INTERNAL_SYSTEM_WINDOW',
    'SET_ACTIVITY_WATCHER', 'WRITE_CONTACTS', 'BIND_VPN_SERVICE',
    'DISABLE_KEYGUARD', 'ACCESS_MOCK_LOCATION', 'GET_PACKAGE_SIZE',
    'MODIFY_PHONE_STATE', 'CHANGE_COMPONENT_ENABLED_STATE', 'CLEAR_APP_CACHE',
    'SET_ORIENTATION', 'READ_CONTACTS', 'DEVICE_POWER', 'HARDWARE_TEST',
    'ACCESS_WIFI_STATE', 'WRITE_EXTERNAL_STORAGE', 'ACCESS_FINE_LOCATION',
    'SET_WALLPAPER_HINTS', 'SET_PREFERRED_APPLICATIONS', 'WRITE_SECURE_SETTINGS',
]


def extract_features(raw_static_result: dict) -> dict:
    """
    Convert StaticAnalysisEngine.analyze() output into a flat numeric
    feature dict matching the real Drebin-115 permission set.

    Args:
        raw_static_result: the dict returned by StaticAnalysisEngine.analyze()

    Returns:
        A dict of {permission_name: 0 or 1}, one entry per FEATURE_NAMES.
    """
    analysis = raw_static_result.get("analysis") or {}
    permissions = analysis.get("permissions", [])

    # APK permissions come as "android.permission.SEND_SMS" — extract the
    # short name to match the dataset's column naming (e.g. "SEND_SMS")
    short_permissions = {p.split(".")[-1] for p in permissions}

    return {name: (1 if name in short_permissions else 0) for name in FEATURE_NAMES}