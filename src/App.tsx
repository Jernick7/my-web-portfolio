/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import Markdown from 'react-markdown';
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, serverTimestamp } from 'firebase/firestore';
import firebaseConfig from '../firebase-applet-config.json';
import { 
  User, 
  Send, 
  Cpu, 
  Rocket, 
  Code2, 
  Music, 
  Gamepad2, 
  Tv, 
  Mail, 
  MessageSquare, 
  Linkedin, 
  Github,
  ChevronRight,
  Terminal,
  Trophy
} from 'lucide-react';
import { GoogleGenAI } from "@google/genai";

// Initialize Gemini API
const genAI = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app, firebaseConfig.firestoreDatabaseId);

const SYSTEM_INSTRUCTIONS = "You are the personal AI assistant for V Jernick Samuel. Jernick is an 18-year-old from India. He studied PCMB in ISC Class 12. His career focus is the intersection of electronics, space, and defense (VLSI, semiconductors, high-power rocketry). He codes in Python, C++, and Verilog. His projects include a Streamlit chore-tracking app, a 3D-printing business plan (Money El), and a writing project called 'The Realm That Should Not Exist' (featuring a character named Edith). His hobbies include Formula 1, football, and music. His father is D. Vijulal Sunil and mother ezhil kiruba brother is Bave v Yohans. Never hallucinate info outside of this context.";

enum OperationType {
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  LIST = 'list',
  GET = 'get',
  WRITE = 'write',
}

interface FirestoreErrorInfo {
  error: string;
  operationType: OperationType;
  path: string | null;
  authInfo: {
    userId?: string | null;
    email?: string | null;
    emailVerified?: boolean | null;
    isAnonymous?: boolean | null;
  }
}

function handleFirestoreError(error: unknown, operationType: OperationType, path: string | null) {
  const errInfo: FirestoreErrorInfo = {
    error: error instanceof Error ? error.message : String(error),
    authInfo: {
      userId: null,
      email: null,
      emailVerified: null,
      isAnonymous: null,
    },
    operationType,
    path
  };
  console.error('Firestore Error: ', JSON.stringify(errInfo));
  throw new Error(JSON.stringify(errInfo));
}

export default function App() {
  const [messages, setMessages] = useState<{ role: 'user' | 'ai'; content: string }[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [visitorName, setVisitorName] = useState('');
  const [visitorEmail, setVisitorEmail] = useState('');
  const [feedback, setFeedback] = useState('');
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = inputValue;
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const model = "gemini-3-flash-preview";
      const result = await genAI.models.generateContent({
        model,
        contents: [...messages.map(m => ({
          role: m.role === 'ai' ? 'model' : 'user',
          parts: [{ text: m.content }]
        })), { role: 'user', parts: [{ text: userMessage }] }],
        config: {
          systemInstruction: SYSTEM_INSTRUCTIONS,
        }
      });

      const responseText = result.text || "I'm sorry, I couldn't process that.";
      setMessages(prev => [...prev, { role: 'ai', content: responseText }]);
    } catch (error) {
      console.error("Gemini API Error:", error);
      setMessages(prev => [...prev, { role: 'ai', content: "SYSTEM ERROR: Could not connect to neural network. Please check API credentials." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingFeedback(true);
    
    try {
      await addDoc(collection(db, 'feedback'), {
        name: visitorName,
        email: visitorEmail,
        content: feedback,
        createdAt: serverTimestamp()
      });
      alert(`Thank you, ${visitorName}! Your insights have been logged to the neural core.`);
      setVisitorName('');
      setVisitorEmail('');
      setFeedback('');
    } catch (error) {
      handleFirestoreError(error, OperationType.WRITE, 'feedback');
    } finally {
      setIsSubmittingFeedback(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-[#f9f9f9] selection:bg-brand-accent selection:text-black">
      {/* Background Elements */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        {/* Grid Pattern */}
        <div 
          className="absolute inset-0 opacity-[0.03]" 
          style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)', backgroundSize: '40px 40px' }}
        />
        
        {/* Glow Spheres */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-accent/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-brand-accent/5 rounded-full blur-[120px]" />

        {/* Diagonal Scanlines */}
        <div className="absolute inset-0 opacity-[0.02] pointer-events-none bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,1)_50%,transparent_75%)] bg-[length:250%_250%] animate-[scan_10s_linear_infinite]" />
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { background-position: 250% 0; }
          100% { background-position: -250% 0; }
        }
      `}} />

      <main className="relative z-10 max-w-3xl mx-auto px-6 py-20 flex flex-col gap-32">
        {/* Section 1: About Me */}
        <motion.section 
          id="about"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="flex flex-col gap-8"
        >
          <div className="flex flex-col gap-4">
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="font-mono text-brand-accent text-sm tracking-widest uppercase"
            >
              Introduction
            </motion.p>
            <h1 className="text-5xl md:text-7xl font-display font-bold tracking-tight leading-tight">
              About <span className="text-gradient">V Jernick Samuel</span>
            </h1>
          </div>

          <div className="glass-glow rounded-3xl p-8 flex flex-col gap-6">
            <p className="text-lg text-white/80 leading-relaxed">
              I am an 18-year-old innovator from <span className="text-white font-medium">India</span>. 
              My journey exists at the high-stakes intersection of <span className="text-brand-accent">electronics, space, and defense</span>. 
              I am deeply immersed in the world of VLSI, semiconductors, and high-power rocketry.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3 p-4 bg-white/5 rounded-2xl border border-white/5">
                <Terminal className="w-5 h-5 text-brand-accent shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium mb-1">Codebase</h3>
                  <p className="text-sm text-white/60">Python, C++, Verilog</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 bg-white/5 rounded-2xl border border-white/5">
                <Rocket className="w-5 h-5 text-brand-accent shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium mb-1">Aerospace</h3>
                  <p className="text-sm text-white/60">High-Power Rocketry & Drones</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 bg-white/5 rounded-2xl border border-white/5">
                <Tv className="w-5 h-5 text-brand-accent shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium mb-1">Entertainment</h3>
                  <p className="text-sm text-white/60 text-balance">Stranger Things, 3 Body Problem, Central Intelligence</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 bg-white/5 rounded-2xl border border-white/5">
                <Gamepad2 className="w-5 h-5 text-brand-accent shrink-0 mt-1" />
                <div>
                  <h3 className="font-medium mb-1">Passions</h3>
                  <p className="text-sm text-white/60">Formula 1, Football, Physics</p>
                </div>
              </div>
            </div>

            <div className="mt-4">
              <p className="font-mono text-xs text-white/40 mb-3 uppercase tracking-tighter">Current Soundtrack</p>
              <div className="overflow-hidden rounded-xl">
                <iframe 
                  style={{ borderRadius: '12px' }} 
                  src="https://open.spotify.com/embed/playlist/3dA8m5G6o4cppV7Cj4BZAH?utm_source=generator&theme=0" 
                  width="100%" 
                  height="152" 
                  frameBorder="0" 
                  allowFullScreen 
                  allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                  loading="lazy"
                ></iframe>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Section 2: AI Assistant */}
        <motion.section 
          id="ai-assistant"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="flex flex-col gap-8"
        >
          <div className="flex flex-col gap-4">
            <p className="font-mono text-brand-accent text-sm tracking-widest uppercase">Intelligent Layer</p>
            <h2 className="text-4xl md:text-5xl font-display font-bold">Ask My <span className="text-gradient">Digital Proxy</span></h2>
            <p className="text-white/60">An AI assistant trained on my biography, projects, and research focus.</p>
          </div>

          <div className="glass rounded-[2rem] overflow-hidden flex flex-col h-[500px]">
            <div className="bg-white/5 p-4 border-bottom border-white/10 flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-brand-accent animate-pulse" />
              <span className="font-mono text-xs uppercase tracking-widest text-white/40">Gemini 1.5 Flash Connected</span>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center gap-4 opacity-40">
                  <MessageSquare className="w-12 h-12" />
                  <p className="text-sm">Initiate secure link to learn about my projects<br/>like <span className="text-brand-accent italic">Money El</span> or <span className="text-brand-accent italic">The Realm That Should Not Exist</span>.</p>
                </div>
              )}
              <AnimatePresence>
                {messages.map((msg, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[85%] p-4 rounded-2xl ${
                      msg.role === 'user' 
                        ? 'bg-brand-accent text-black rounded-tr-none font-medium' 
                        : 'bg-white/10 text-white/90 rounded-tl-none border border-white/5'
                    }`}>
                      {msg.role === 'user' ? (
                        msg.content
                      ) : (
                        <div className="markdown-body prose prose-invert prose-sm max-w-none">
                          <Markdown>{msg.content}</Markdown>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/5 p-4 rounded-2xl rounded-tl-none border border-white/5 flex gap-1">
                    <div className="w-1.5 h-1.5 bg-brand-accent rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-1.5 h-1.5 bg-brand-accent rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-1.5 h-1.5 bg-brand-accent rounded-full animate-bounce" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="p-4 bg-black/40 backdrop-blur-md border-t border-white/10 flex gap-2">
              <input 
                type="text" 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask about VLSI or my 3D printing business..."
                className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-brand-accent/50 transition-colors"
                id="chat-input"
              />
              <button 
                onClick={handleSendMessage}
                disabled={isLoading}
                className="bg-brand-accent text-black p-3 rounded-xl hover:scale-105 active:scale-95 transition-transform disabled:opacity-50 disabled:scale-100"
                id="send-button"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </motion.section>

        {/* Section 3: Contact Form */}
        <motion.section 
          id="contact"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="flex flex-col gap-8 mb-20"
        >
          <div className="flex flex-col gap-4">
            <p className="font-mono text-brand-accent text-sm tracking-widest uppercase">Identity Verification</p>
            <h2 className="text-4xl md:text-5xl font-display font-bold">Leave a <span className="text-gradient">Trace</span></h2>
            <p className="text-white/60">Share your thoughts or feedback on my build.</p>
          </div>

          <form onSubmit={handleFeedbackSubmit} className="glass-glow rounded-[2rem] p-8 md:p-12 flex flex-col gap-8">
            <div className="flex flex-col gap-2">
              <label htmlFor="visitor-name" className="text-xs uppercase tracking-widest text-white/40 font-mono">Your Name</label>
              <input 
                required
                type="text" 
                id="visitor-name"
                value={visitorName}
                onChange={(e) => setVisitorName(e.target.value)}
                placeholder="Agent 001"
                className="bg-white/5 border-b border-white/20 py-4 focus:outline-none focus:border-brand-accent transition-colors text-xl font-display"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="visitor-email" className="text-xs uppercase tracking-widest text-white/40 font-mono">Your Email (for replies)</label>
              <input 
                required
                type="email" 
                id="visitor-email"
                value={visitorEmail}
                onChange={(e) => setVisitorEmail(e.target.value)}
                placeholder="agent@intel.com"
                className="bg-white/5 border-b border-white/20 py-4 focus:outline-none focus:border-brand-accent transition-colors text-xl font-display"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="feedback" className="text-xs uppercase tracking-widest text-white/40 font-mono">What do you know about me? / Feedback</label>
              <textarea 
                required
                id="feedback"
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="I heard you're building Edith..."
                rows={4}
                className="bg-white/5 border-b border-white/20 py-4 focus:outline-none focus:border-brand-accent transition-colors text-lg resize-none"
              />
            </div>

            <button 
              type="submit"
              disabled={isSubmittingFeedback}
              className="bg-brand-accent text-black font-display font-bold py-6 rounded-2xl flex items-center justify-center gap-3 hover:gap-5 transition-all text-xl disabled:opacity-50 disabled:scale-95"
              id="submit-feedback"
            >
              {isSubmittingFeedback ? 'Syncing...' : 'Submit Intelligence'} <ChevronRight className="w-6 h-6" />
            </button>
          </form>
        </motion.section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-6">
        <div className="max-w-3xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8 text-white/30 text-sm font-mono">
          <p>© 2026 V JERNICK SAMUEL. ALL SYSTEMS NOMINAL.</p>
          <div className="flex gap-6">
            <a href="https://www.linkedin.com/in/jernick7" target="_blank" rel="noreferrer" className="hover:text-brand-accent transition-colors">LINKEDIN</a>
            <a href="https://www.instagram.com/jernick7/" target="_blank" rel="noreferrer" className="hover:text-brand-accent transition-colors">INSTAGRAM</a>
            <a href="https://github.com/Jernick7" target="_blank" rel="noreferrer" className="hover:text-brand-accent transition-colors">GITHUB</a>
            <a href="mailto:jernick77@gmail.com" className="hover:text-brand-accent transition-colors">GMAIL</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
