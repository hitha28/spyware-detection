rule Spyware_Generic
{
    meta:
        author = "SpySentinel Team"
        description = "Placeholder generic spyware rule"

    strings:
        $spy = "spy"
        $track = "track"

    condition:
        any of them
}