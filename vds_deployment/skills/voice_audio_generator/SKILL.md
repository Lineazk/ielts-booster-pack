---
name: voice_audio_generator
description: Generates high-fidelity correct pronunciation audio (.mp3) files locally/free for IELTS vocabulary lists and updates the JSON database.
version: 1.0.0
tools:
  - name: generate_word_pronunciation
    description: Generate pre-uploaded pronunciation audio for a specific vocabulary word.
    command: python run_generator.py --word "{word}"
  - name: compile_entire_vault_audio
    description: Pre-compile correct pronunciation audios for all words inside the IELTS vocabulary pack preview.
    command: python run_generator.py --all
---

# Skill: Voice Pronunciation Audio Generator

This skill enables the autonomous AI agent or user to locally generate and pre-compile high-fidelity correct pronunciation `.mp3` files for IELTS advanced vocabulary lists. 

## 📖 Instructions for Agent
1. When the user asks to *"generate audio guide for [word]"* or *"pre-upload pronunciation"* or *"compile pronunciation database"*, execute the corresponding tool command.
2. The audios are generated natively using a free public TTS pipeline stream without requiring any premium API keys, ensuring $0 running cost.
