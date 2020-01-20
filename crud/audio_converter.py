import moviepy.editor as mp
from pydub import AudioSegment
import os

def video_to_audio(videopath):
    wavaudiopath=videopath.replace('.mp4','.wav')
    clip = mp.VideoFileClip(videopath)
    clip.audio.write_audiofile(wavaudiopath)
    fullpath = os.path.join(os.getcwd(), wavaudiopath)
    song = AudioSegment.from_wav(fullpath)
    flacaudiopath=fullpath.replace('.wav','.flac')
    song.export(flacaudiopath,format = "flac")
    return flacaudiopath