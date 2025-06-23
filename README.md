# Solconverter

This project provides a FastAPI backend that accepts an MP3 upload and
returns a solfège transcription. It combines Magenta's Onsets & Frames model
for audio transcription, Music21 for key detection and solfège mapping and an
OpenAI GPT model to format the final notation.

## Setup

1. Install the dependencies:

```bash
pip install -r requirements.txt
```

2. Download an Onsets & Frames checkpoint and set `ONSETS_FRAMES_CKPT` to the
   path of the checkpoint file.

3. Provide your OpenAI API key via `OPENAI_API_KEY` environment variable.

## Running the server

Start the FastAPI application using `uvicorn`:

```bash
uvicorn main:app --reload
```

Then POST an MP3 file to `http://localhost:8000/transcribe/` and you will get
JSON containing the solfège notation.
