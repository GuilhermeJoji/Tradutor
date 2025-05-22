# -*- coding: utf-8 -*-
"""
Created on Thu May 22 18:32:49 2025

@author: guijoji
"""
import streamlit as st
import os
import tempfile
import whisper
import argostranslate.package
import argostranslate.translate
import subprocess
import shlex

# Funções auxiliares
def formatar_tempo(segundos):
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    ms = int((segundos % 1) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def gerar_srt(transcription, srt_path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segmento in enumerate(transcription['segments']):
            start = formatar_tempo(segmento['start'])
            end = formatar_tempo(segmento['end'])
            text = segmento['text']
            f.write(f"{i + 1}\n{start} --> {end}\n{text}\n\n")

def traduzir_srt(original, traduzido, idioma_origem, idioma_destino):
    with open(original, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    with open(traduzido, "w", encoding="utf-8") as f_out:
        for linha in linhas:
            if "-->" in linha or linha.strip().isdigit() or linha.strip() == "":
                f_out.write(linha)
            else:
                texto_traduzido = argostranslate.translate.translate(linha.strip(), idioma_origem, idioma_destino)
                f_out.write(texto_traduzido + "\n")

def adicionar_legenda(video_path, srt_path, output_path):
    cmd = f"ffmpeg -i {shlex.quote(video_path)} -vf subtitles={shlex.quote(srt_path)} {shlex.quote(output_path)}"
    subprocess.run(cmd, shell=True)

# Interface Streamlit
st.title("Tradutor de Vídeos com Legenda")
idiomas = ["pt", "en", "es"]

idioma_origem = st.selectbox("Selecione o idioma de origem", idiomas)
idioma_destino = st.selectbox("Selecione o idioma de destino", idiomas)
video_file = st.file_uploader("Faça upload do vídeo (.mp4)", type=["mp4"])

if st.button("Processar vídeo") and video_file:
    with tempfile.TemporaryDirectory() as tempdir:
        video_path = os.path.join(tempdir, "video.mp4")
        with open(video_path, "wb") as f:
            f.write(video_file.read())

        audio_path = os.path.join(tempdir, "audio.mp3")
        srt_path = os.path.join(tempdir, "legenda.srt")
        srt_traduzido = os.path.join(tempdir, f"legenda_{idioma_destino}.srt")
        video_leg = os.path.join(tempdir, f"video_legendado_{idioma_destino}.mp4")

        st.info("Carregando modelo de transcrição...")
        modelo = whisper.load_model("medium")

        st.info("Extraindo áudio...")
        subprocess.run(['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path], check=True)

        st.info("Transcrevendo...")
        resultado = modelo.transcribe(audio_path, language=idioma_origem)

        st.info("Gerando .srt...")
        gerar_srt(resultado, srt_path)

        st.info("Instalando pacotes de tradução...")
        argostranslate.package.update_package_index()
        pacotes = argostranslate.package.get_available_packages()
        pacote = next(p for p in pacotes if p.from_code == idioma_origem and p.to_code == idioma_destino)
        argostranslate.package.install_from_path(pacote.download())

        st.info("Traduzindo legenda...")
        traduzir_srt(srt_path, srt_traduzido, idioma_origem, idioma_destino)

        st.info("Adicionando legenda ao vídeo...")
        adicionar_legenda(video_path, srt_traduzido, video_leg)

        st.success("Processo concluído! Baixe o vídeo abaixo.")
        with open(video_leg, "rb") as f:
            st.download_button("Download do vídeo legendado", f, file_name=f"video_legendado_{idioma_destino}.mp4")

