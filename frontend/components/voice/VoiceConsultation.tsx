"use client";

import React, { useState } from "react";
import { createConsultation } from "../../services/consultationService";

const SpeechRecognition =
  typeof window !== "undefined"
    ? (window as any).webkitSpeechRecognition ||
      (window as any).SpeechRecognition
    : null;

export default function VoiceConsultation() {
  const [transcript, setTranscript] = useState("");
  const [isListening, setIsListening] = useState(false);

  const startListening = () => {
    if (!SpeechRecognition) {
      alert("Speech Recognition API is not supported in this browser.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event: any) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        interim += event.results[i][0].transcript;
      }
      setTranscript(interim);
    };
    recognition.onend = () => {
      setIsListening(false);
      if (transcript) {
        // send to backend for storage
        createConsultation({
          input_type: "voice",
          transcription: transcript,
          raw_input: transcript,
        }).catch((err) => console.error("consultation save failed", err));
      }
    };
    recognition.start();
  };

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-xl font-semibold">Voice Input (Web Speech API)</h2>
      <button
        onClick={startListening}
        disabled={isListening}
        className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50"
      >
        {isListening ? "Listening..." : "Start Recording"}
      </button>
      <p className="text-sm">{transcript || "Transcript will appear here"}</p>
    </div>
  );
}
