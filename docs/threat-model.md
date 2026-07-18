# SpySentinel — Threat Model

## What we're detecting
Spyware and stalkerware on Android apps (APK) and Windows executables (PE),
plus suspicious network behavior (beaconing, unusual DNS activity).

## In scope
- Known spyware families via hash/YARA signature matching
- Dangerous permission combinations in Android apps (e.g. mic + location +
  network access together)
- Suspicious Windows API usage (keylogging, screen capture, process
  injection, credential access)
- Packed/obfuscated executables (a common spyware evasion technique)
- Unknown spyware, via an ML classifier trained on permission/behavior patterns

## Out of scope (for this POC)
- iOS spyware
- Kernel-level rootkits
- Real-time enterprise fleet deployment
- Full deep packet payload inspection
- Auto-removal/remediation of detected threats

## Assumptions
- The scanned file is provided directly by the user (upload), not pulled
  from a live, potentially compromised device
- Network capture requires the user to run the tool with elevated
  (root/admin) privileges
- The ML model is trained on public research datasets, not live production
  malware — detection accuracy reflects that

## Known limitations
- Static analysis can be evaded by heavy obfuscation beyond what our packer
  heuristics catch
- The ML classifier's accuracy is bounded by the size/quality of the public
  training dataset used
- No sandboxing/dynamic execution — we never run the scanned file, only
  inspect it statically