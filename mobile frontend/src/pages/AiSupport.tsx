import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import ChatMessage from '../components/ChatMessage';
import { generateAiResponse, type Message } from '../lib/mockAi';

const AiSupport = () => {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: 'Hello! I am your AI courier assistant. How can I help you today? \n\nආයුබෝවන්! මම ඔබේ AI කුරියර් සහායකයා. මට ඔබට උදව් කළ හැක්කේ කෙසේද?',
            sender: 'ai',
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            text: input,
            sender: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        const responseText = await generateAiResponse(userMsg.text);

        const aiMsg: Message = {
            id: (Date.now() + 1).toString(),
            text: responseText,
            sender: 'ai',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, aiMsg]);
        setIsTyping(false);
    };

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <header className="bg-white p-4 shadow-sm sticky top-0 z-10">
                <h1 className="text-lg font-bold text-gray-800">AI Support Agent</h1>
                <p className="text-xs text-gray-500">Supports Sinhala & English</p>
            </header>

            <div className="flex-1 overflow-y-auto p-4">
                {messages.map(msg => (
                    <ChatMessage key={msg.id} message={msg} />
                ))}
                {isTyping && (
                    <div className="flex items-center gap-2 text-gray-400 text-sm ml-10 mb-4">
                        <span className="animate-bounce">●</span>
                        <span className="animate-bounce delay-100">●</span>
                        <span className="animate-bounce delay-200">●</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-gray-200">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Type a message... / පණිවිඩයක් ටයිප් කරන්න..."
                        className="flex-1 p-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isTyping}
                        className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send size={20} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AiSupport;
