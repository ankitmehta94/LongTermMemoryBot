CREATE TABLE Transcriptions (
    id SERIAL PRIMARY KEY,
    transcription TEXT,
    user_id CHAR(12),
    transcription_type CHAR(12) NULL
);