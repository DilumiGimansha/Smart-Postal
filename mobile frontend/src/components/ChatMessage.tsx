import clsx from 'clsx';
import type { Message } from '../lib/mockAi';
import { Bot, User } from 'lucide-react';

interface ChatMessageProps {
    message: Message;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
    const isAi = message.sender === 'ai';

    return (
        <div className={clsx("flex w-full mb-4", isAi ? "justify-start" : "justify-end")}>
            <div className={clsx("flex max-w-[80%] items-end gap-2", isAi ? "flex-row" : "flex-row-reverse")}>
                <div className={clsx(
                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                    isAi ? "bg-blue-100 text-blue-600" : "bg-gray-100 text-gray-600"
                )}>
                    {isAi ? <Bot size={18} /> : <User size={18} />}
                </div>

                <div className={clsx(
                    "p-3 rounded-2xl text-sm shadow-sm",
                    isAi ? "bg-white text-gray-800 rounded-bl-none border border-gray-100" : "bg-blue-600 text-white rounded-br-none"
                )}>
                    {message.text}
                    <div className={clsx("text-[10px] mt-1 opacity-70", isAi ? "text-gray-400" : "text-blue-100")}>
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatMessage;
