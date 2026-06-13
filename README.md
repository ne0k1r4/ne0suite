# ne0suite

One entry point for the whole security toolchain. Instead of remembering
seven different invocations and install steps, one dispatcher.

## what this should be

- `ne0suite status` - what's installed and what isn't
- `ne0suite <tool> [args...]` - dispatch to a tool
- short aliases, because typing `lightscan` every single time is silly
- one install script that sets everything up

Still a sketch. The tools it routes to already exist as separate projects.
