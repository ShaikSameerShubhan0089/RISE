import React, { useState } from 'react';
import { Volume2, VolumeX, Loader2 } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

/**
 * Reusable VoiceButton component for Text-to-Speech support.
 * @param {string} content - The text content to be read aloud.
 */
const VoiceButton = ({ content, className = '' }) => {
    const { speak } = useLanguage();
    const [isSpeaking, setIsSpeaking] = useState(false);

    const handleSpeak = () => {
        if (!content) return;

        setIsSpeaking(true);
        speak(content);

        // Browser Speech API doesn't always have a robust 'onend' across all browsers,
        // but we can simulate the state change.
        setTimeout(() => setIsSpeaking(false), 3000);
    };

    return (
        <button
            onClick={handleSpeak}
            disabled={!content}
            className={`p-1.5 rounded-lg transition-colors hover:bg-indigo-50 text-indigo-600 disabled:opacity-30 disabled:cursor-not-allowed ${className}`}
            title="Listen to data"
        >
            {isSpeaking ? (
                <VolumeX className="w-4 h-4 animate-pulse" />
            ) : (
                <Volume2 className="w-4 h-4" />
            )}
        </button>
    );
};

export default VoiceButton;
