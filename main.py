# FastAPI application to transcribe MP3 files using Magenta Onsets & Frames
# Requires: fastapi, pydub, magenta (or note_seq), music21, openai

import json
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydub import AudioSegment
from music21 import converter, key

# OpenAI is optional so we don't fail at import time if the package isn't
# installed. We'll raise a clear error later if it is required.
try:
    import openai
except Exception:
    openai = None

# Magenta / note_seq imports for transcription
try:
    from note_seq.protobuf import music_pb2
    from note_seq import midi_io
    from note_seq.onsets_frames_transcription import infer_util
except Exception:
    # Fallback if note_seq is unavailable
    music_pb2 = None
    midi_io = None
    infer_util = None

app = FastAPI()

SOLFA = {1: "Do", 2: "Re", 3: "Mi", 4: "Fa", 5: "Sol", 6: "La", 7: "Ti"}


def transcribe_wav(wav_path: str, checkpoint: str) -> "music_pb2.NoteSequence":
    """Transcribe a WAV file to a NoteSequence using Magenta."""
    if not infer_util:
        raise RuntimeError("note_seq or Magenta not installed")
    return infer_util.transcribe_audio(wav_path, checkpoint)


def parse_midi(midi_path: str):
    """Parse MIDI with music21 and return note events with timing and solfège."""
    score = converter.parse(midi_path)
    analysed_key = score.analyze('key')
    events = []
    for n in score.flat.notes:
        if n.isNote:
            t = float(n.offset)
            solfa = SOLFA.get(analysed_key.getScaleDegreeFromPitch(n.pitch) or 1)
            events.append({
                "time": t,
                "note": n.nameWithOctave,
                "duration": float(n.quarterLength),
                "solfa": solfa,
            })
    return events


@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    if file.content_type != 'audio/mpeg':
        raise HTTPException(status_code=400, detail="Only MP3 files are supported")

    with tempfile.TemporaryDirectory() as tmpdir:
        mp3_path = os.path.join(tmpdir, 'input.mp3')
        wav_path = os.path.join(tmpdir, 'input.wav')
        midi_path = os.path.join(tmpdir, 'output.mid')

        with open(mp3_path, 'wb') as f:
            f.write(await file.read())

        # Convert MP3 to WAV
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format='wav')

        # Transcribe to NoteSequence and save MIDI
        ckpt = os.getenv("ONSETS_FRAMES_CKPT", "onsets_frames.ckpt")
        sequence = transcribe_wav(wav_path, ckpt)
        if not midi_io:
            raise RuntimeError("note_seq not installed to write MIDI")
        midi_io.sequence_proto_to_midi_file(sequence, midi_path)

        events = parse_midi(midi_path)

    prompt = (
        "Group these notes into 4/4 bars and annotate durations (quarter, half, whole, etc.). "
        "Return only the bar-divided solfège syllables.\n" +
        json.dumps(events)
    )

    if not openai:
        raise HTTPException(status_code=500, detail="openai package not installed")

    openai.api_key = os.getenv('OPENAI_API_KEY')
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        notation = resp.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"notation": notation})

