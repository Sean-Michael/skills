# Curated Expo-Compatible Libraries

> Load when selecting libraries for a new project or feature.
> All entries are Expo SDK compatible and work with `expo run:ios` local builds.

## Navigation
- `expo-router` — file-based routing, recommended default
- `@react-navigation/native` + `@react-navigation/native-stack` — manual setup, more control

## State Management
- `zustand` — global state, minimal boilerplate
- `@tanstack/react-query` — server state, caching, background refetch
- `jotai` — atomic state, good for fine-grained reactivity

## Styling
- `nativewind` — Tailwind utility classes in RN (requires setup in babel.config.js)
- `react-native-unistyles` — typed StyleSheet with theming
- `@shopify/restyle` — design system primitives

## UI Components
- `react-native-paper` — Material Design, well-maintained
- `tamagui` — fast, themeable, Expo-compatible
- `@gluestack-ui/themed` — accessible, composable

## Forms
- `react-hook-form` — best-in-class, works in RN
- `zod` — schema validation, pair with react-hook-form

## Networking
- `axios` — HTTP client
- `@tanstack/react-query` — data fetching layer (use with axios or fetch)

## Storage
- `expo-secure-store` — encrypted key-value (tokens, secrets)
- `@react-native-async-storage/async-storage` — unencrypted key-value
- `expo-sqlite` — local SQLite database
- `mmkv` — fast key-value (requires dev build, not Expo Go)

## Auth
- `expo-auth-session` — OAuth flows
- `expo-local-authentication` — Face ID / Touch ID

## Media
- `expo-image-picker` — camera roll + camera access
- `expo-camera` — direct camera control
- `expo-av` — audio/video playback
- `expo-image` — optimized image component (better than RN Image)

## Native Device
- `expo-location` — GPS
- `expo-notifications` — push + local notifications
- `expo-haptics` — haptic feedback
- `expo-sensors` — accelerometer, gyroscope, etc.
- `expo-clipboard` — clipboard read/write

## Maps
- `react-native-maps` — Google/Apple Maps (requires native rebuild)
- `expo-location` — for coordinates

## Animations
- `react-native-reanimated` — high-performance animations (Expo-compatible)
- `moti` — declarative animations built on reanimated

## Icons
- `@expo/vector-icons` — included with Expo, covers Ionicons/FontAwesome/etc.
- `lucide-react-native` — clean icon set

## Testing
- `jest` + `jest-expo` — unit/integration testing
- `@testing-library/react-native` — component testing

## Utilities
- `date-fns` — date manipulation
- `expo-constants` — app.json values at runtime
- `expo-linking` — deep links + universal links
- `expo-sharing` — native share sheet

## Notes on native rebuilds

Libraries with native code require `expo run:ios` rebuild (not just Metro restart) when first added:
- `react-native-maps`
- `expo-camera` (first add)
- `mmkv`
- `react-native-reanimated` (first add)
- Any `expo-*` module with native code

When in doubt: `npx expo-doctor` will tell you if a rebuild is needed.
