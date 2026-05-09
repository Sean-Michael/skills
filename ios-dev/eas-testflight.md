# EAS Build + TestFlight Submission

> Load this reference when the user is ready to submit to TestFlight or the App Store.
> Not needed for local simulator development.

## Prerequisites

- Apple Developer account ($99/yr)
- App registered in App Store Connect
- EAS account: `npm install -g eas-cli && eas login`

## First-time EAS setup

```bash
eas build:configure
# Creates eas.json — commit this
```

`eas.json` baseline:
```json
{
  "cli": { "version": ">= 10.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": false }
    },
    "production": {
      "ios": { "buildConfiguration": "Release" }
    }
  },
  "submit": {
    "production": {}
  }
}
```

## Version bump before every submission

In `app.json`:
- `version`: bump semver (1.0.0 → 1.0.1) for App Store releases
- `ios.buildNumber`: bump integer string ("1" → "2") for every TestFlight upload

Apple requires buildNumber to strictly increase. They do NOT require version to change
between TestFlight builds, but it's good practice to keep them meaningful.

## TestFlight (internal testing)

```bash
eas build --platform ios --profile preview
# Wait for build (~10-20min)
eas submit --platform ios --latest
# Or submit manually via App Store Connect with the .ipa
```

## App Store submission

```bash
# Bump version + buildNumber in app.json first
eas build --platform ios --profile production
eas submit --platform ios --latest
```

Then in App Store Connect:
1. Add the build to your app version
2. Fill out What's New
3. Submit for Review

## Certificates

EAS manages provisioning profiles and signing certs automatically via `credentialsSource: "remote"`.
Don't manually manage these unless you have a specific reason.

If you get cert errors: `eas credentials` to inspect/reset.
