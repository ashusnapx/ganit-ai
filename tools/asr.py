from faster_whisper import WhisperModel

# Load once (important for performance)
MODEL = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

CONFIDENCE_THRESHOLD = 0.75


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribes audio and highlights low-confidence words.
    Returns raw text, highlighted HTML, and average confidence.
    """

    segments, info = MODEL.transcribe(
        audio_path,
        beam_size=5,
        language="en",
        word_timestamps=True
    )

    full_text = []
    highlighted = []
    confidences = []

    for segment in segments:
        if not segment.words:
            continue

        for word in segment.words:
            word_text = word.word.strip()
            if not word_text:
                continue

            prob = word.probability if word.probability is not None else 0.5
            confidences.append(prob)

            if prob < CONFIDENCE_THRESHOLD:
                highlighted.append(
                    f"<span style='background-color:#FFF3A3'>{word_text}</span>"
                )
            else:
                highlighted.append(word_text)

            full_text.append(word_text)

    avg_confidence = (
        sum(confidences) / len(confidences)
        if confidences else 0.0
    )

    return {
        "raw_text": " ".join(full_text),
        "highlighted_html": " ".join(highlighted),
        "confidence": round(avg_confidence, 3)
    }
