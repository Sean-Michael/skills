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

## Validation Loop

Run after every feature. Do not declare done until all pass.

```bash
npx tsc --noEmit           # must be clean
npx expo-doctor            # must be clean
xcrun simctl boot "iPhone 16" 2>/dev/null || true && open -a Simulator
npx expo run:ios --device "iPhone 16"
```

Then screenshot-drive every screen and feature:
```bash
screencapture -x /tmp/sim.png                        # capture
xcrun simctl io booted tap <x> <y>                   # tap
xcrun simctl io booted swipe <x1> <y1> <x2> <y2>    # swipe
xcrun simctl io booted type "text"                   # type
```

For each screen: navigate → screenshot → verify renders → tap every interactive element → screenshot → verify result. Check empty/loading/error states.

Repeat on iPhone SE:
```bash
xcrun simctl boot "iPhone SE (3rd generation)" && npx expo run:ios --device "iPhone SE (3rd generation)"
```

**Sign-off checklist:**
- [ ] `tsc --noEmit` clean
- [ ] `expo-doctor` clean
- [ ] Launches without crash on iPhone 16 and iPhone SE sims
- [ ] Every screen renders correctly (screenshot verified)
- [ ] Every interactive element works (tap + screenshot verified)
- [ ] No Metro console errors
- [ ] Auth flow works: sign in, protected route gating, sign out
- [ ] Data screens load real Supabase data

## Footguns

- **Native rebuild**: adding native-code library after first `expo run:ios` requires re-running it, not just restarting Metro
- **Safe area**: root needs `<SafeAreaProvider>`, screens need `<SafeAreaView>` — missing = content under notch
- **Keyboard**: text input screens need `<KeyboardAvoidingView behavior="padding">`
- **Expo Go**: some libraries don't work in Expo Go; always use `expo run:ios` dev builds

## References

- `references/eas-testflight.md` — TestFlight/App Store submission when ready
- `references/common-libraries.md` — curated Expo-compatible library list
- `references/plugin-architecture.md` — recommended structure for extensible apps
