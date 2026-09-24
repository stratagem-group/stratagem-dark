-- STRATAGEM DARK Hyprland setup: helpers, defaults, and current theme overrides.

require("default.hypr.helpers")
local require_optional = require("default.hypr.require_optional")

-- Use STRATAGEM DARK defaults, but don't edit these directly.
require("default.hypr.autostart")
if _G.stratagem_default_bindings ~= false then
  require("default.hypr.bindings.media")
  require("default.hypr.bindings.clipboard")
  require("default.hypr.bindings.tiling")
  require("default.hypr.bindings.utilities")


end
require("default.hypr.envs")
require("default.hypr.looknfeel")
require("default.hypr.qconsole")
require("default.hypr.input")
require("default.hypr.windows")

-- Current theme overrides.
require_optional.module("stratagem.current.theme.hyprland")
