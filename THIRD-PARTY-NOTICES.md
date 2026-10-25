# Third-party notices

WaughForm 3D (© 2026 David John Waugh, GNU GPL v3 or later) includes the following work by others. Each keeps its own licence.

## Manifold geometry library

- Used for the Enclosure Wizard's solid modelling (the `manifold-3d` package, version 3.5.4). It is built into `WaughForm_3D.html`.
- © The Manifold Authors. Licensed under the **Apache License 2.0**.
- Source: https://github.com/elalish/manifold
- Licence text: [`vendor/manifold-3d/LICENSE`](vendor/manifold-3d/LICENSE)

## Anthropic TypeScript SDK

- Used for the optional "Look up online" feature (`@anthropic-ai/sdk`, version 1.3.0). It is bundled for the browser and built into `WaughForm_3D.html`.
- © Anthropic. Licensed under the **Apache License 2.0**.
- Source: https://github.com/anthropics/anthropic-sdk-typescript
- Licence text: [`vendor/anthropic-sdk/LICENSE`](vendor/anthropic-sdk/LICENSE)

## Fritzing parts library

- The parts library that comes with WaughForm 3D ([`desktop/parts-library.json`](desktop/parts-library.json): over 2,000 parts with their pins, sizes, descriptions and pictures) is made from the Fritzing parts library.
- © Fritzing contributors. Licensed under **Creative Commons Attribution-ShareAlike 3.0** (CC BY-SA 3.0): https://creativecommons.org/licenses/by-sa/3.0/
- Source: https://github.com/fritzing/fritzing-parts
- The parts were converted into WaughForm 3D's format: pins, sizes and pictures were extracted, and descriptions were cleaned.
- The converted library is shared under the same CC BY-SA 3.0 licence, not the GPL.
- Parts made from it, or brought in with "Import pins…", keep this credit in their notes. Anyone sharing them must keep the credit and the same licence.

## Electron

- The Windows app is built with Electron (MIT licence, © GitHub Inc. and Electron contributors), which includes Chromium and other open-source components.
- Their licences are copied into the app's folder by the build: `LICENSE.electron.txt` and `LICENSES.chromium.html`.
