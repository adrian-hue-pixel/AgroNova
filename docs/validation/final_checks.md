# Language voice and parameter verification

Verified on 4 November 2026 against https://agronova-intelligence.streamlit.app . Model: gemini-3.5-flash-lite.

## Controlled parameter experiment

The same engineered prompt and system instruction were used for three runs. Temperature 0.3 and token limit 8192 produced a complete 260-word answer. Changing only temperature to 0.9 produced a complete 282-word answer and different suggested actions. Changing only the token limit to 256 cut off the answer during the Overview, and the app displayed a truncation warning. One observation per setting does not establish accuracy or statistically measure variability. Keep the 8192-token production budget for the structured answer. Raw results: parameter_checks.json.

## Twelve answer languages

All twelve calls returned text without API errors or the app's truncation warning: English, Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Bengali, French, Spanish, Portuguese and Twi. The responses use the requested scripts/languages while keeping the five parsing headings in English. This verifies language routing and output presence, not expert-certified translation quality or agronomic accuracy. Twi and other less familiar translations warrant fluent-speaker review. Raw results: language_checks.json.

## Tamil audio and reply

A synthetic recording, generated with the installed Vani Tamil voice, said: “என் தக்காளி செடியின் இலைகள் மஞ்சளாக உள்ளன. நான் என்ன பார்க்க வேண்டும்?” The deployed audio-upload flow transcribed the Tamil words correctly, with punctuation omitted. With the sidebar still in English and Ask by Voice set to Automatic, the answer body appeared in Tamil and the page displayed “Answer language: Tamil”. This exercises the real Gemini transcription and answer services, rather than mocks. It does not exercise the user's physical microphone or accent. Raw evidence: tamil_voice.json.

Read-aloud uses the browser's device voices. The test browser reported no matching Tamil voice. The player now waits briefly for voices to load and, if none matches, explains the missing voice without reading Tamil using a mismatched default voice. Spoken playback on the user's device still depends on that device offering a Tamil voice.

## Theme and navigation

Fresh visits start in dark mode, including the native Streamlit theme. The in-app switch keeps light mode available. Light mode has CSS animations for drifting leaves, floating pollen and soft moving glows. The live browser showed 16 pollen elements and active leaf-drift/pollen-rise animations. Low-data mode removed the background layer. Reduced-motion preferences also disable repeating motion. A visual check exposed low-contrast controls in the current Streamlit React Aria widgets; the theme CSS now targets those controls directly.

## Automated checks

60 unit tests passed. 142 mocked page scenarios passed, including a fresh-visit dark-mode assertion and explicit light-mode visits. These checks complement the live tests and do not replace physical microphone or device-specific speech checks.
