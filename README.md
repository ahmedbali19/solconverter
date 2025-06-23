# Solconverter

This project provides a FastAPI backend that accepts an MP3 upload and
returns a solfège transcription. It combines Magenta's Onsets & Frames model
for audio transcription, Music21 for key detection and solfège mapping and an
OpenAI GPT model to format the final notation.

## Setup

1. Install the dependencies (including `python-multipart` for file uploads):

```bash
pip install -r requirements.txt
```

2. Download an Onsets & Frames checkpoint and set `ONSETS_FRAMES_CKPT` to the
   path of the checkpoint file.

3. Create a `.env` file with your OpenAI API key:

   ```bash
   echo "OPENAI_API_KEY=YOUR_KEY" > .env
   ```

## Running the server

Start the FastAPI application using `uvicorn`:

```bash
uvicorn main:app --reload
```

Then POST an MP3 file to `http://localhost:8000/transcribe/` and you will get
JSON containing the solfège notation.

You can also open `index.html` in a browser to record or upload an audio file
and see the transcription using the frontend.

## GitHub Pages

The repository includes a workflow in `.github/workflows/pages.yml` that
publishes the static frontend through GitHub Pages. The workflow now
attempts to automatically enable Pages during the build. If Pages are not
yet configured for the repository, the workflow will enable them and deploy
the site. Once Pages is enabled, every push to `main` will deploy the latest
`index.html` and `script.js` files.
