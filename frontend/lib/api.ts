const rawUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_URL = rawUrl.replace(/\/+$/, "");

export interface ChatVerse {
    chapter: number;
    verse: number;
    text: string;
    shloka?: string;
    transliteration?: string;
    hindi_translation?: string;
}

export interface ChatResponse {
    response: string;
    relevant_verses: ChatVerse[];
    language: string;
}

export async function sendMessage(
    message: string,
    language: string,
    mood: string
): Promise<ChatResponse> {
    const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message, language, mood }),
    });

    if (!res.ok) {
        if (res.status === 429) {
            throw new Error("You are meditating too quickly. Please wait a moment.");
        }
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned ${res.status}. Please try again.`);
    }

    return res.json();
}
