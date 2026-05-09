# Plugin Architecture

Structure apps so new features never touch core — prevents regressions when Claude adds features.

```
src/
  core/        # Shell, navigation, providers — set once, rarely touch
  plugins/
    auth/      # Self-contained: screens + logic + types
    feed/
    settings/
  shared/      # Shared components, hooks, utils
```

Each plugin is self-contained. New feature = new plugin folder. Core registers plugins via a central index. Claude's edits stay scoped to one plugin at a time.
