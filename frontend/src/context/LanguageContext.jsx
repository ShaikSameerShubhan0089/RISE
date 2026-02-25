import React, { createContext, useContext, useState, useEffect } from 'react';
import { translations } from '../constants/translations';

const LanguageContext = createContext(null);

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within LanguageProvider');
    }
    return context;
};

export const LanguageProvider = ({ children }) => {
    const [language, setLanguage] = useState(localStorage.getItem('language') || 'en');
    const isRTL = language === 'ur';

    useEffect(() => {
        localStorage.setItem('language', language);
        document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
        document.documentElement.lang = language;
    }, [language, isRTL]);

    // Helper to get translated text
    const t = (path) => {
        const keys = path.split('.');
        let result = translations[language];
        for (const key of keys) {
            if (!result || !result[key]) {
                // Return English version if key is missing in selected language
                let fallback = translations.en;
                for (const fk of keys) {
                    if (!fallback) break;
                    fallback = fallback[fk];
                }
                return fallback || path;
            }
            result = result[key];
        }
        return result;
    };

    const speak = (text) => {
        if (!window.speechSynthesis) return;

        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        // Map app language to BCP 47
        const langMap = {
            en: 'en-IN',
            te: 'te-IN',
            hi: 'hi-IN',
            kn: 'kn-IN',
            ur: 'ur-IN',
            ta: 'ta-IN'
        };
        utterance.lang = langMap[language] || 'en-IN';

        // Try to find a female voice
        const voices = window.speechSynthesis.getVoices();
        const femaleVoice = voices.find(v =>
            (v.name.toLowerCase().includes('female') ||
                v.name.toLowerCase().includes('google') ||
                v.name.toLowerCase().includes('samantha') ||
                v.name.toLowerCase().includes('zira') ||
                v.name.toLowerCase().includes('heera')) &&
            v.lang.startsWith(language)
        );

        if (femaleVoice) {
            utterance.voice = femaleVoice;
        }

        utterance.rate = 0.9;
        utterance.pitch = 1.1; // Slightly higher pitch for "sweetness"

        window.speechSynthesis.speak(utterance);
    };

    const value = {
        language,
        setLanguage,
        isRTL,
        t,
        speak
    };

    return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};
