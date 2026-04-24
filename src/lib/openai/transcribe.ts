import { getOpenAIClient } from "./client";

export async function transcribeAudio(
  audioBuffer: Buffer,
  filename: string = "audio.webm"
): Promise<string> {
  const openai = getOpenAIClient();

  const uint8 = new Uint8Array(audioBuffer);
  const file = new File([uint8], filename, { type: "audio/webm" });

  const transcription = await openai.audio.transcriptions.create({
    file,
    model: "whisper-1",
    language: "ar",
  });

  return transcription.text;
}
