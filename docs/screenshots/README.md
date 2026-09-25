# Screenshots and demo capture

The main README links to these exact file names. Drop the files into this folder and they'll show up there.

| File | What to capture |
|---|---|
| `chat-answer.png` | The chat answering a service question from the knowledge base (e.g. "Do you do SEO for clinics?") |
| `chat-guardrail.png` | The chat refusing to quote a price and offering a call back instead |
| `chat-callback.png` | The chat collecting name, number and time, then confirming the call back |
| `voice-widget.png` | The ElevenLabs voice widget open on the website, mid-conversation |
| `lead-alert.png` | The Slack alert or the new HubSpot deal the call back created (blur the name and number) |
| `demo.gif` | 20–40 seconds: one chat exchange, then one short voice exchange |

Before you commit a capture:

- Use a test name and a dummy number, never a real visitor's.
- Crop out the browser address bar if it shows the n8n host or the hosted-chat URL.
- Blur the ElevenLabs agent id if the dashboard is in frame.
- The secret scanner skips this folder because it can't read images, so check these by eye.

Tools: ScreenToGif (Windows) or Kap (macOS) for the GIF. Keep it under 10 MB so GitHub renders it inline.
