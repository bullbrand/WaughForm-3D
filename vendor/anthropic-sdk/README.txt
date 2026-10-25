Anthropic TypeScript SDK (@anthropic-ai/sdk 1.3.0, Apache License 2.0 - see LICENSE), bundled for the browser
so WaughForm 3D can call Claude for the optional "Look up online" feature. Sets window.AnthropicSDK.

To rebuild after updating the SDK (in an empty folder):
  npm install @anthropic-ai/sdk esbuild
  node node_modules\esbuild\install.js
  (copy entry.js from here)
  node node_modules\esbuild\bin\esbuild entry.js --bundle --minify --format=iife --platform=browser --target=chrome120 --legal-comments=eof --outfile=anthropic-sdk.js
Copy anthropic-sdk.js here, then in the "claude code" folder run:  node tools\embed-anthropic.js
