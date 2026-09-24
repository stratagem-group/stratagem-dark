-- STRATAGEM DARK policy: no upstream provisioning, uploads or background updates.
hl.on("hyprland.start", function()
  hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP STRATAGEM_DARK_PATH")
  hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
  hl.exec_cmd("stratagem-launch-shell")
  hl.exec_cmd("swaybg -i /usr/share/stratagem-dark/branding/wallpaper.png -m fill")
end)
