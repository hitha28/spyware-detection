rule Spyware_Generic
{
    meta:
        author = "SpySentinel Team"
        description = "Generic heuristic: combination of surveillance-related API strings"
        severity = "medium"

    strings:
        $sms_read = "READ_SMS"
        $sms_send = "SEND_SMS"
        $call_log = "READ_CALL_LOG"
        $location = "ACCESS_FINE_LOCATION"
        $record_audio = "RECORD_AUDIO"
        $camera = "CAMERA"
        $hidden_icon = "LAUNCHER_CATEGORY_HIDDEN"

    condition:
        3 of them
}