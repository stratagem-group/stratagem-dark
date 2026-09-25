# STRATAGEM DARK alpha4 corrections

Alpha3 hardware feedback reported repeated Wi-Fi credential prompts, unusable tool entries, a skipped login screen and missing boot branding. Alpha3's successful simulated WPA2 test did not establish physical Wi-Fi reliability; help/version smoke tests did not establish functional tool workflows.

- Personal Wi-Fi activation and saved reconnect now share one private-profile path. Missing saved credentials return to the inline form. Explicit attempts disable autoconnect until successful, and secrets remain profile-owned rather than delegated to another secret agent. Enterprise credentials still use the advanced editor; no certificate validation is weakened. Physical reproduction of the reported second prompt remains required.
- Tool entries offer a working terminal, literal argument execution and help. The launcher does not invent targets, execute argument text as a shell command, or elevate itself. Packet capture and other privileged operations still require appropriate permissions.
- The live image stops at an original SDDM username/password screen using the existing vector wordmark and real PAM authentication. The public live test credentials remain stratagem / stratagem. Autologin is removed.
- An original Plymouth theme displays the same wordmark during graphical boot. Display firmware and early kernel output may precede the splash.

New acceptance gates exercise rejected and successful SDDM login, wrong Wi-Fi password recovery, a usable tool terminal, and actual Nmap/YARA/radare2/ExifTool operations on local fixtures. Existing entry-point checks remain smoke tests, not a claim that all BlackArch tools have been fully validated.

The SDDM and Plymouth theme code is Stratagem-owned. The upstream API references are https://github.com/sddm/sddm/wiki/Theming and Plymouth's script theme interface. Existing Omarchy code attribution and adapted-file hashes remain in THIRD_PARTY_NOTICES.md and provenance/imports.json.
