---
name: ios-dev
description: >
  Use for any mobile app task: building, modifying, testing, or deploying with
  Expo + React Native. Triggers: mobile app, iOS app, React Native, Expo,
  simulator, TestFlight, App Store, expo run, app.json. Core rule: never hand
  off without completing the validation loop. The human's only job is UI/UX feel.
---

# iOS Development Skill (Expo + React Native)

## Stack

- React Native via Expo SDK (latest stable), TypeScript strict
- Build: `npx expo run:ios` (local builds, no EAS)
- Navigation: Expo Router (preferred)
- Backend: Supabase (always — see supabase/postgres skills for schema/RLS/migrations)
- State: Zustand + React Query
- Styling: NativeWind or StyleSheet — pick one per project, stay consistent

## Project Setup

```bash
npx create-expo-app@latest <app-name> --template blank-typescript
npx expo install expo-router react-native-safe-area-context react-native-screens
```

Set `"strict": true` in tsconfig. Configure `app.json` `bundleIdentifier`, `version: "1.0.0"`, `ios.buildNumber: "1"`. Install all required libraries before writing features.

**Version discipline** — Apple rejects without this: `version` is semver, bump manually per App Store release. `ios.buildNumber` increments per TestFlight upload. Expo never auto-bumps either.

## Supabase Wiring (RN-specific only)

The supabase skill handles everything else. These three things differ from web:

**1. Install**
```bash
npx expo install @supabase/supabase-js @react-native-async-storage/async-storage \
  expo-secure-store expo-auth-session expo-web-browser
```

**2. Client config** — `SecureStore` adapter + `detectSessionInUrl: false` (breaks auth without it):
```typescript
import { createClient } from '@supabase/supabase-js'
import * as SecureStore from 'expo-secure-store'

export const supabase = createClient(
  process.env.EXPO_PUBLIC_SUPABASE_URL!,   // EXPO_PUBLIC_ prefix required
  process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!,
  {
    auth: {
      storage: { getItem: SecureStore.getItemAsync, setItem: SecureStore.setItemAsync, removeItem: SecureStore.deleteItemAsync },
      autoRefreshToken: true, persistSession: true,
      detectSessionInUrl: false,
    },
  }
)
```

**3. OAuth** — web redirect flow doesn't work in RN:
```typescript
import * as AuthSession from 'expo-auth-session'
import * as WebBrowser from 'expo-web-browser'
WebBrowser.maybeCompleteAuthSession()

const redirectUri = AuthSession.makeRedirectUri({ scheme: 'your-scheme' })
const { data } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: { redirectTo: redirectUri, skipBrowserRedirect: true },
})
if (data.url) await WebBrowser.openAuthSessionAsync(data.url, redirectUri)
```
Register `scheme` in `app.json`. Register redirect URI in Supabase dashboard → Auth → URL Configuration.

**Storage uploads** — direct URI doesn't work, read via `expo-file-system` as base64 first.

## Targeting a Simulator by Name

```bash
npx expo run:ios --simulator "iPhone 17 Pro"   # simulator — use --simulator, NOT --device
# --device targets physical devices and requires code signing
```

Boot + open:
```bash
xcrun simctl boot "iPhone 17 Pro" 2>/dev/null || true && open -a Simulator
```

## Simulator Interaction

**`xcrun simctl io booted tap` does NOT exist.** Do not attempt it.

Options for driving UI without touch injection:

**1. Debugger-driven navigation (preferred for validation)**

Wire up a `globalThis.__navigateTo` helper in `__DEV__` so the Metro debugger can drive navigation and read/write Zustand state without UI interaction:

```typescript
// App.tsx or root layout — DEV only
import { createNavigationContainerRef } from '@react-navigation/native';
export const navigationRef = createNavigationContainerRef<any>();

if (__DEV__) {
  (globalThis as any).__navigateTo = (name: string) => {
    if (navigationRef.isReady()) navigationRef.navigate(name as never);
  };
}
```

Connect from Node.js:
```javascript
const WebSocket = require('ws');
// get device id: GET http://localhost:8081/json
const ws = new WebSocket('ws://localhost:8081/inspector/debug?device=<id>&page=1');
ws.on('open', () => {
  ws.send(JSON.stringify({
    id: 1, method: 'Runtime.evaluate',
    params: { expression: '__navigateTo("ProfileScreen")' }
  }));
});
```

Use `Runtime.evaluate` to call `__navigateTo`, read/write Zustand stores, assert UI state.

**2. `xcrun simctl io booted screenshot <path>`** — always works, any process:
```bash
xcrun simctl io booted screenshot /tmp/sim.png
```

**3. Physical mouse clicks on Simulator** — only when Simulator is frontmost app.

**4. `xcrun simctl io booted sendPasteboard` + keyboard shortcut** — for text input.

## Validation Loop

Run after every feature. Do not declare done until all pass.

```bash
npx tsc --noEmit           # must be clean
npx expo-doctor            # must be clean
xcrun simctl boot "iPhone 17 Pro" 2>/dev/null || true && open -a Simulator
npx expo run:ios --simulator "iPhone 17 Pro"
```

For each screen: navigate (via debugger or manual click) → screenshot → verify renders → exercise interactive elements → screenshot → verify result. Check empty/loading/error states.

```bash
xcrun simctl io booted screenshot /tmp/sim.png
```

Repeat on iPhone SE:
```bash
xcrun simctl boot "iPhone SE (3rd generation)" 2>/dev/null || true
npx expo run:ios --simulator "iPhone SE (3rd generation)"
```

**Sign-off checklist:**
- [ ] `tsc --noEmit` clean
- [ ] `expo-doctor` clean
- [ ] Launches without crash on iPhone 17 Pro and iPhone SE sims
- [ ] Every screen renders correctly (screenshot verified)
- [ ] Every interactive element works (tap + screenshot verified, or debugger-driven)
- [ ] No Metro console errors
- [ ] Auth flow works: sign in, protected route gating, sign out
- [ ] Data screens load real Supabase data

## Footguns

- **Native rebuild**: adding a native-code library requires re-running `expo run:ios`, not just restarting Metro. Same applies to changes to `babel.config.js` — module IDs change at the native boundary. Rule: anything that affects the Metro module graph at the native boundary needs a full rebuild.
- **`--simulator` vs `--device`**: use `--simulator "iPhone 17 Pro"` to target a sim by name. `--device` targets physical devices and will trigger code signing prompts if one is paired.
- **Safe area**: root needs `<SafeAreaProvider>`, screens need `<SafeAreaView>` — missing = content under notch
- **Keyboard**: text input screens need `<KeyboardAvoidingView behavior="padding">`
- **Expo Go**: some libraries don't work in Expo Go; always use `expo run:ios` dev builds
- **babel-preset-expo**: use `babel-preset-expo`, not `@react-native/babel-preset` — the latter causes crashes

## References

- `references/eas-testflight.md` — TestFlight/App Store submission when ready
- `references/common-libraries.md` — curated Expo-compatible library list
- `references/plugin-architecture.md` — recommended structure for extensible apps
