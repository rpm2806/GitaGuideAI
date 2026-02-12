"use client";

import { useState, useEffect, useRef } from "react";
import {
    Send, User, Bot, Globe, Heart,
    ChevronDown, ChevronUp,
    BookOpen, Sun, Moon
} from "lucide-react";
import { sendMessage } from "../lib/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Message = {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: string;
    verses?: Array<{
        chapter: number; verse: number; text: string;
        shloka?: string; transliteration?: string; hindi_translation?: string;
    }>;
    showVerses?: boolean;
};

const MOODS = ["Neutral", "Sad", "Anxious", "Angry", "Confused", "Seeking Purpose", "Grief"];
const LANGUAGES = [
    { code: "en", name: "English" },
    { code: "hi", name: "Hindi" },
];

const getTime = () => new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

export default function ChatInterface() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [mood, setMood] = useState("Neutral");
    const [language, setLanguage] = useState("en");
    const [isDarkMode, setIsDarkMode] = useState(false);
    const endRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const headerRef = useRef<HTMLElement>(null);
    const footerRef = useRef<HTMLDivElement>(null);
    const [headerH, setHeaderH] = useState(80);
    const [footerH, setFooterH] = useState(110);

    // ── Measure header/footer ──
    useEffect(() => {
        const measure = () => {
            if (headerRef.current) setHeaderH(headerRef.current.offsetHeight);
            if (footerRef.current) setFooterH(footerRef.current.offsetHeight);
        };
        measure();
        window.addEventListener('resize', measure);
        return () => window.removeEventListener('resize', measure);
    }, []);

    // ── Theme ──
    useEffect(() => {
        const s = localStorage.getItem("gita-theme");
        if (s === "dark") { setIsDarkMode(true); document.documentElement.setAttribute("data-theme", "dark"); }
    }, []);
    const toggleTheme = () => {
        const n = !isDarkMode; setIsDarkMode(n);
        document.documentElement.setAttribute("data-theme", n ? "dark" : "light");
        localStorage.setItem("gita-theme", n ? "dark" : "light");
    };

    // ── Language ──
    useEffect(() => { const s = localStorage.getItem("gita-lang"); if (s) setLanguage(s); }, []);
    useEffect(() => { localStorage.setItem("gita-lang", language); }, [language]);

    // ── Scroll ──
    useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isLoading]);

    // ── Send ──
    const handleSend = async () => {
        if (!input.trim() || isLoading) return;
        const userMsg: Message = { id: Date.now().toString(), role: "user", content: input, timestamp: getTime() };
        setMessages(p => [...p, userMsg]); setInput(""); setIsLoading(true);
        try {
            const data = await sendMessage(input, language, mood);
            setMessages(p => [...p, {
                id: (Date.now() + 1).toString(), role: "assistant",
                content: data.response, verses: data.relevant_verses, showVerses: false, timestamp: getTime()
            }]);
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : "Unknown error";
            setMessages(p => [...p, {
                id: Date.now().toString(), role: "assistant", timestamp: getTime(),
                content: `I'm having difficulty right now. Please try again. (${errorMessage})`,
            }]);
        } finally { setIsLoading(false); inputRef.current?.focus(); }
    };

    const toggleVerses = (id: string) =>
        setMessages(p => p.map(m => m.id === id ? { ...m, showVerses: !m.showVerses } : m));

    // ════════════════════ RENDER ════════════════════
    return (
        <div style={{ height: '100vh', background: 'var(--bg-page)', position: 'relative', overflow: 'hidden' }}>

            {/* ── Animated Background ── */}
            <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 0 }}>
                <div className="animate-breathe" style={{ position: 'absolute', top: '-20%', left: '-10%', width: '50%', height: '50%', borderRadius: '50%', background: 'var(--purple)', opacity: 0.06, filter: 'blur(120px)' }} />
                <div className="animate-breathe" style={{ position: 'absolute', bottom: '-15%', right: '-10%', width: '60%', height: '60%', borderRadius: '50%', background: 'var(--orange)', opacity: 0.05, filter: 'blur(100px)', animationDelay: '4s' }} />
                <div className="animate-float" style={{ position: 'absolute', top: '20%', left: '30%', width: 6, height: 6, borderRadius: '50%', background: 'var(--purple)', opacity: 0.3 }} />
                <div className="animate-float" style={{ position: 'absolute', top: '60%', right: '25%', width: 8, height: 8, borderRadius: '50%', background: 'var(--orange)', opacity: 0.2, animationDelay: '2s' }} />
                <div className="animate-float" style={{ position: 'absolute', top: '40%', left: '70%', width: 5, height: 5, borderRadius: '50%', background: 'var(--amber)', opacity: 0.25, animationDelay: '3s' }} />
            </div>

            {/* ══════ HEADER ══════ */}
            <header ref={headerRef} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap',
                padding: '14px 24px', background: 'var(--bg-white)', borderBottom: '2px solid var(--border)',
                position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50, gap: 12
            }}>
                {/* Logo */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    <div style={{
                        width: 48, height: 48, borderRadius: 14, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: isDarkMode ? 'linear-gradient(135deg, #7c3aed, #6d28d9)' : 'linear-gradient(135deg, var(--orange), #d97706)', color: '#fff', fontSize: 26, fontWeight: 700,
                        boxShadow: '0 4px 14px var(--shadow)', border: '2px solid rgba(255,255,255,0.2)'
                    }}>ॐ</div>
                    <div>
                        <h1 style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-dark)', letterSpacing: '-0.3px', lineHeight: 1.2 }}>
                            GitaGuide AI
                        </h1>
                        <p style={{ fontSize: 11, color: 'var(--text-light)', fontWeight: 500, letterSpacing: 1.5, textTransform: 'uppercase', marginTop: 2 }}>
                            Spiritual Companion
                        </p>
                    </div>
                </div>

                {/* Controls */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>

                    <button onClick={toggleTheme} title={isDarkMode ? "Light Mode" : "Dark Mode"} style={{
                        padding: 10, borderRadius: 12, border: '2px solid var(--border)', background: 'var(--bg-grey)',
                        color: 'var(--text-dark)', cursor: 'pointer', display: 'flex', alignItems: 'center',
                        transition: 'all 0.2s'
                    }}>
                        {isDarkMode ? <Sun size={20} color="#f59e0b" /> : <Moon size={20} />}
                    </button>

                    <div style={{
                        display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px', borderRadius: 12,
                        border: '2px solid var(--border)', background: 'var(--bg-grey)'
                    }}>
                        <Heart size={18} color="var(--orange)" />
                        <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-light)', textTransform: 'uppercase', letterSpacing: 1 }}>Mood:</span>
                        <select value={mood} onChange={e => setMood(e.target.value)} style={{
                            background: 'transparent', border: 'none', fontSize: 14, fontWeight: 600,
                            color: 'var(--text-dark)', cursor: 'pointer', outline: 'none'
                        }}>
                            {MOODS.map(m => <option key={m} value={m} style={{ background: '#fff', color: '#1a1a1a' }}>{m}</option>)}
                        </select>
                    </div>

                    <div style={{
                        display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px', borderRadius: 12,
                        border: '2px solid var(--border)', background: 'var(--bg-grey)'
                    }}>
                        <Globe size={18} color="var(--purple)" />
                        <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-light)', textTransform: 'uppercase', letterSpacing: 1 }}>Lang:</span>
                        <select value={language} onChange={e => setLanguage(e.target.value)} style={{
                            background: 'transparent', border: 'none', fontSize: 14, fontWeight: 600,
                            color: 'var(--text-dark)', cursor: 'pointer', outline: 'none'
                        }}>
                            {LANGUAGES.map(l => <option key={l.code} value={l.code} style={{ background: '#fff', color: '#1a1a1a' }}>{l.name}</option>)}
                        </select>
                    </div>
                </div>
            </header>

            {/* ══════ MESSAGES ══════ */}
            <div style={{ position: 'fixed', top: headerH, bottom: footerH, left: 0, right: 0, overflowY: 'auto', overflowX: 'hidden', padding: '24px 16px', zIndex: 1 }}>
                <div style={{ maxWidth: 760, margin: '0 auto' }}>

                    {/* Empty State */}
                    {messages.length === 0 && (
                        <div className="animate-msg" style={{ textAlign: 'center', paddingTop: '15vh' }}>
                            <div style={{
                                width: 100, height: 100, borderRadius: '50%', margin: '0 auto 20px',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                background: 'linear-gradient(135deg, var(--orange), #d97706)', color: '#fff',
                                fontSize: 52, fontWeight: 700, boxShadow: '0 8px 30px var(--shadow)'
                            }}>ॐ</div>
                            <h2 style={{ fontSize: 36, fontWeight: 700, color: 'var(--text-dark)', marginBottom: 6 }}>GitaGuide AI</h2>
                            <p style={{ fontSize: 22, color: 'var(--text-dark)', marginBottom: 4 }}>Pranam 🙏</p>
                            <p style={{ fontSize: 15, color: 'var(--text-medium)', maxWidth: 420, margin: '0 auto 8px', lineHeight: 1.6 }}>
                                I am here to guide you through the eternal wisdom of the Bhagavad Gita.
                            </p>
                            <p style={{ fontSize: 14, color: 'var(--orange)', fontWeight: 500 }}>What weighs upon your mind today?</p>

                            <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap', marginTop: 28 }}>
                                {["What is my purpose?", "How to find peace?", "Dealing with anxiety"].map(q => (
                                    <button key={q} onClick={() => { setInput(q); inputRef.current?.focus(); }} style={{
                                        padding: '10px 20px', borderRadius: 50, fontSize: 13, fontWeight: 600,
                                        border: '2px solid var(--purple)', color: 'var(--purple)', background: 'var(--purple-light)',
                                        cursor: 'pointer', transition: 'all 0.2s'
                                    }}
                                        onMouseEnter={e => { e.currentTarget.style.background = 'var(--purple)'; e.currentTarget.style.color = '#fff'; }}
                                        onMouseLeave={e => { e.currentTarget.style.background = 'var(--purple-light)'; e.currentTarget.style.color = 'var(--purple)'; }}>
                                        {q}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Message Bubbles */}
                    {messages.map(msg => {
                        const isUser = msg.role === "user";
                        return (
                            <div key={msg.id} className="animate-msg"
                                style={{ display: 'flex', flexDirection: 'column', alignItems: isUser ? 'flex-end' : 'flex-start', marginBottom: 16 }}>

                                {/* Avatar + Name Row */}
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexDirection: isUser ? 'row-reverse' : 'row' }}>
                                    <div style={{
                                        width: 32, height: 32, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        background: isUser ? 'linear-gradient(135deg, #7c3aed, #a78bfa)' : 'linear-gradient(135deg, var(--orange), #d97706)',
                                        color: '#fff', fontSize: 14, fontWeight: 600, flexShrink: 0
                                    }}>
                                        {isUser ? <User size={16} /> : <Bot size={16} />}
                                    </div>
                                    <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-light)' }}>
                                        {isUser ? "You" : "GitaGuide"}
                                    </span>
                                </div>

                                {/* Bubble */}
                                <div style={{
                                    maxWidth: '78%', padding: '14px 18px', lineHeight: 1.65, fontSize: 15,
                                    borderRadius: isUser ? '20px 20px 6px 20px' : '20px 20px 20px 6px',
                                    background: isUser ? 'linear-gradient(135deg, #7c3aed, #6d28d9)' : 'var(--bg-grey)',
                                    color: isUser ? '#fff' : 'var(--text-dark)',
                                    boxShadow: '0 2px 8px var(--shadow)', wordBreak: 'break-word'
                                }}>
                                    {isUser ? (
                                        <span>{msg.content}</span>
                                    ) : (
                                        <ReactMarkdown remarkPlugins={[remarkGfm]}
                                            components={{
                                                p: ({ ...props }) => <p style={{ color: 'inherit', margin: '4px 0', lineHeight: 1.65 }} {...props} />,
                                                strong: ({ ...props }) => <strong style={{ color: 'var(--orange)', fontWeight: 700 }} {...props} />,
                                                em: ({ ...props }) => <em style={{ color: 'inherit', opacity: 0.8 }} {...props} />,
                                                li: ({ ...props }) => <li style={{ color: 'inherit', marginLeft: 16 }} {...props} />,
                                            }}>
                                            {msg.content}
                                        </ReactMarkdown>
                                    )}
                                </div>

                                {/* Timestamp */}
                                <span style={{ fontSize: 11, color: 'var(--text-light)', marginTop: 4, padding: '0 4px' }}>
                                    {msg.timestamp}
                                </span>

                                {/* Verses + Listen (assistant only) */}
                                {!isUser && msg.verses && msg.verses.length > 0 && (
                                    <div style={{ marginTop: 6, maxWidth: '78%' }}>
                                        <button onClick={() => toggleVerses(msg.id)} style={{
                                            display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 20,
                                            border: '1.5px solid var(--purple)', background: 'var(--purple-light)', color: 'var(--purple)',
                                            fontSize: 12, fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s'
                                        }}>
                                            <BookOpen size={14} />
                                            {msg.showVerses ? "Hide Verses" : `${msg.verses.length} Sacred Verse${msg.verses.length > 1 ? 's' : ''}`}
                                            {msg.showVerses ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                                        </button>

                                        {msg.showVerses && (
                                            <div className="animate-msg" style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}>
                                                {msg.verses.map((v, i) => (
                                                    <div key={i} style={{
                                                        padding: '14px 16px', borderRadius: 14, border: '1.5px solid var(--border)',
                                                        background: 'var(--bg-white)', position: 'relative', overflow: 'hidden'
                                                    }}>

                                                        <p style={{ fontWeight: 700, fontSize: 13, color: 'var(--orange)', marginBottom: 6 }}>
                                                            Chapter {v.chapter}, Verse {v.verse}
                                                        </p>
                                                        {v.shloka && <p style={{ fontSize: 15, fontStyle: 'italic', color: 'var(--text-dark)', marginBottom: 6, opacity: 0.85 }}>{v.shloka}</p>}
                                                        {v.transliteration && <p style={{ fontSize: 12, color: 'var(--text-light)', marginBottom: 6, fontStyle: 'italic' }}>{v.transliteration}</p>}
                                                        <p style={{ fontSize: 14, color: 'var(--text-medium)', fontStyle: 'italic', borderLeft: '3px solid var(--orange)', paddingLeft: 12 }}>
                                                            &quot;{v.text}&quot;
                                                        </p>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                )}


                            </div>
                        );
                    })}

                    {/* Typing Indicator */}
                    {isLoading && (
                        <div className="animate-msg" style={{ display: 'flex', alignItems: 'flex-end', gap: 8, marginBottom: 16 }}>
                            <div style={{
                                width: 32, height: 32, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                background: 'linear-gradient(135deg, var(--orange), #d97706)', color: '#fff'
                            }}><Bot size={16} /></div>
                            <div style={{
                                padding: '14px 20px', borderRadius: '20px 20px 20px 6px', background: 'var(--bg-grey)',
                                display: 'flex', gap: 6, alignItems: 'center'
                            }}>
                                {[0, 0.15, 0.3].map((d, i) => (
                                    <span key={i} style={{
                                        width: 8, height: 8, borderRadius: '50%', background: 'var(--text-light)',
                                        animation: `pulse-dot 1.4s ${d}s ease-in-out infinite`, display: 'inline-block'
                                    }} />
                                ))}
                            </div>
                        </div>
                    )}

                    <div ref={endRef} />
                </div>
            </div>

            {/* ══════ INPUT BAR ══════ */}
            <div ref={footerRef} style={{
                padding: '14px 20px', background: 'var(--bg-white)', borderTop: '2px solid var(--border)',
                position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 50
            }}>
                <div style={{ maxWidth: 760, margin: '0 auto', display: 'flex', alignItems: 'center', gap: 12, padding: '8px 8px 8px 16px', borderRadius: 50, border: '2px solid var(--border)', background: isDarkMode ? '#1e293b' : '#f1f0fb' }}>
                    <input ref={inputRef} type="text" value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === "Enter" && handleSend()}
                        placeholder="Ask about the Gita..."
                        disabled={isLoading}
                        style={{
                            flex: 1, padding: '13px 20px', borderRadius: 50, border: 'none',
                            fontSize: 15, background: 'transparent', color: 'var(--text-dark)', outline: 'none'
                        }} />

                    <button onClick={handleSend} disabled={isLoading || !input.trim()} title="Send"
                        style={{
                            width: 46, height: 46, borderRadius: '50%', border: 'none', cursor: 'pointer',
                            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, transition: 'all 0.2s',
                            background: input.trim() ? 'linear-gradient(135deg, #7c3aed, #6d28d9)' : 'var(--bg-grey)',
                            color: input.trim() ? '#fff' : 'var(--text-light)',
                            opacity: isLoading ? 0.5 : 1
                        }}>
                        <Send size={20} />
                    </button>
                </div>
                <p style={{ textAlign: 'center', fontSize: 10, color: 'var(--text-light)', marginTop: 8, letterSpacing: 1.5, textTransform: 'uppercase' }}>
                    AI guidance • Verify with scripture
                </p>
            </div>
        </div>
    );
}
