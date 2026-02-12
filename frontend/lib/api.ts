const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatResponse {
    response: string;
    relevant_verses: Array<{
        chapter: number;
        verse: number;
        text: string;
    }>;
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
        throw new Error(errorData.detail || "Failed to reach the guru.");
    }

    return res.json();
}
