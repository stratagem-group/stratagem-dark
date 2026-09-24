# Tool catalog

This is an intentionally small candidate catalog. `arch` denotes an official Arch
package candidate (the release lock must resolve its exact repository); `blackarch`
is an optional adapter. Package existence, dependency closure and licenses must be
verified against the selected snapshot before release. Repository choice never
silently falls back to AUR or a different supplier. All licenses remain NOASSERTION
until reviewed; the project is not redistributing these packages now.

Schemas validate shape; `dark validate` also checks graph and uniqueness constraints.
Only a future release builder may promote reviewed entries into a signed lock.
