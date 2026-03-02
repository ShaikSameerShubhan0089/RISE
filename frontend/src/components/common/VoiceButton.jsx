import React, { useState } from 'react';
import { Volume2, VolumeX, Loader2 } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

/**
 * Reusable VoiceButton component for Text-to-Speech support.
 * @param {string} content - The text content to be read aloud.
 */
const VoiceButton = ({ content, className = '' }) => {
    const { speak, t } = useLanguage();
    const [isSpeaking, setIsSpeaking] = useState(false);

    const handleToggleSpeak = () => {
        if (!content) return;

        if (isSpeaking) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
        } else {
            setIsSpeaking(true);
            speak(content);

            // Periodically check if speaking is finished
            const checkSpeaking = setInterval(() => {
                if (!window.speechSynthesis.speaking) {
                    setIsSpeaking(false);
                    clearInterval(checkSpeaking);
                }
            }, 500);
        }
    };

    return (
        <button
            onClick={handleToggleSpeak}
            disabled={!content}
            className={`p-1.5 rounded-lg transition-all active:scale-95 hover:bg-indigo-50 text-indigo-600 disabled:opacity-30 disabled:cursor-not-allowed ${className}`}
            title={isSpeaking ? t('voice_ui.stop_listening') : t('voice_ui.listen_summary')}
        >
            {isSpeaking ? (
                <div className="flex items-center gap-1">
                    <VolumeX className="w-4 h-4 animate-bounce" />
                    <span className="text-[10px] font-bold uppercase tracking-tighter">{t('voice_ui.stop')}</span>
                </div>
            ) : (
                <Volume2 className="w-4 h-4" />
            )}
        </button>
    );
};

export default VoiceButton;
