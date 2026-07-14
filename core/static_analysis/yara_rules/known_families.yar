rule Known_Spyware_Family
{
    meta:
        author = "SpySentinel Team"
        description = "Placeholder known spyware family rule"

    strings:
        $family = "Pegasus"

    condition:
        $family
}
