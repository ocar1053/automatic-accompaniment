import shutil
from basic_pitch.inference import predict_and_save
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydub import AudioSegment
from pathlib import Path
import os
from auto_accompany.song_convert import convert_to_midi
from data_process.generatemusic import generate_music
app = FastAPI()


app.mount("/static", StaticFiles(directory="C:/Users/Hsieh/Documents/nccucs/specialTopic/special_topic/src/api/"), name="static")


origins = [
    "http://192.168.1.103:8080",
    "http://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # ensure is .wav format
        if not file.filename.endswith(".wav"):
            raise HTTPException(
                status_code=400, detail="Invalid file format. Only .wav files are accepted.")

        # create upload folder if not exists
        upload_folder = Path("uploaded_files")
        upload_folder.mkdir(exist_ok=True)

        #  temp safe file to disk
        temp_file = upload_folder / "temp.wav"
        with temp_file.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        sound = AudioSegment.from_wav(temp_file)

        # chcek if stereo
        if sound.channels == 1:

            sound = sound.set_channels(2)

        #  save file
        output_path = upload_folder / "wqeqweqwe.wav"
        sound.export(output_path, format="wav")

        # delete temp file
        os.remove(temp_file)

        return {"filename": file.filename, "channels": sound.channels}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.get("/process")
async def process_file():
    script_directory = Path(__file__).resolve().parent
    vocal_file = script_directory / "uploaded_files" / "wqeqweqwe.wav"
    vocal_midi_output = os.path.join(script_directory, "midi", "wqeqweqwe.mid")
    try:
        convert_to_midi(vocal_file, vocal_midi_output)
        generate_music(vocal_file, vocal_midi_output)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    return {"status": "success"}
