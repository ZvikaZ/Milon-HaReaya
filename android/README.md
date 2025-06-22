# Milon Android App

A minimal Android WebView app that displays the Milon website with a custom Hebrew toolbar.

## Prerequisites

- Android SDK
- Java/JDK
- Required credentials files in `key/` directory (see Setup section)

## Setup

1. **Keystore Configuration**: Ensure `keystore.properties` contains:
   ```
   storePassword=YOUR_KEYSTORE_PASSWORD
   keyPassword=YOUR_KEY_PASSWORD
   keyAlias=YOUR_KEY_ALIAS
   storeFile=key/keystore
   ```

2. **Google Play Upload Configuration**: 
   - Download JSON service account credentials from Google Cloud Console
   - Save as `key/service-account.json`

## Essential Commands

### Development

```bash
# Clean project
./gradlew clean

# Build debug APK for testing
./gradlew assembleDebug
# Output: app/build/outputs/apk/debug/app-debug.apk

# Install debug APK to connected device
./gradlew installDebug
```

### Release

```bash
# Build signed release APK for Google Play
./gradlew assembleRelease
# Output: app/build/outputs/apk/release/app-release.apk

# Build and upload to Google Play  
./gradlew publishReleaseApk
```

### Other Useful Commands

```bash
# Check for lint issues
./gradlew lint

# Run tests
./gradlew test

# List all available tasks
./gradlew tasks

# Build both debug and release
./gradlew build
```

## File Structure

```
android/
├── app/
│   ├── build.gradle          # App configuration and dependencies
│   ├── src/main/
│   │   ├── AndroidManifest.xml
│   │   ├── java/.../MainActivity.java
│   │   └── res/              # Resources (layouts, icons, etc.)
├── key/                      # ⚠️ NOT in git - contains sensitive files
│   ├── keystore             # Signing keystore
│   └── service-account.json # Google Play API credentials
├── keystore.properties      # ⚠️ NOT in git - signing configuration
└── README.md               # This file
```

## Important Notes

- **Keystore Security**: All signing keys and passwords are excluded from git
- **Upload Status**: Google Play upload uses official Gradle plugin with APK format
- **WebView Configuration**: App loads `http://18.159.236.82/milon` with JavaScript enabled
- **Minimum SDK**: Android API 26 (Android 8.0+)
- **Target SDK**: Android API 35

## Troubleshooting

### Build Issues
- Ensure Android SDK path is correctly set in `local.properties`
- Check that keystore file exists and passwords are correct

### Upload Issues
- Ensure `key/service-account.json` is valid and accessible
- Verify the service account has Google Play publishing permissions
- Check that the APK file was built successfully before upload

### WebView Issues
- Verify internet connectivity
- Check if the target URL is accessible
- Review WebView settings in MainActivity.java

## App Features

- Custom Hebrew toolbar: "מילון הראיה"
- WebView with JavaScript and DOM storage enabled
- Search functionality works within the web interface
- Prevents external browser opening (stays within app)
- Minimal permissions (only INTERNET required)