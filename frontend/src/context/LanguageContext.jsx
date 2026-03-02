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
            ur: 'ur-PK',  // Pakistan variant for Urdu
            ta: 'ta-IN'
        };
        utterance.lang = langMap[language] || 'en-IN';

        // Enhanced voice selection: prioritize quality female voices
        const voices = window.speechSynthesis.getVoices();
        let selectedVoice = null;

        // Priority 1: Look for explicitly sweet/female Google voices
        selectedVoice = voices.find(v => {
            const name = v.name.toLowerCase();
            return (
                v.lang.startsWith(language) && (
                    name.includes('female') ||
                    name.includes('woman') ||
                    name.includes('girl') ||
                    name.includes('zira') ||  // Microsoft Zira (English, excellent quality)
                    name.includes('heera') ||  // Hindi
                    name.includes('noto') ||  // Google voices
                    name.includes('neural')
                )
            );
        });

        // Priority 2: Google Wavenet/Neural voices (high quality)
        if (!selectedVoice) {
            selectedVoice = voices.find(v =>
                v.lang.startsWith(language) &&
                (v.name.includes('Google') || v.name.includes('Neural'))
            );
        }

        // Priority 3: Microsoft voices (good quality)
        if (!selectedVoice) {
            selectedVoice = voices.find(v =>
                v.lang.startsWith(language) &&
                v.name.includes('Microsoft')
            );
        }

        // Priority 4: Any voice with matching language
        if (!selectedVoice) {
            selectedVoice = voices.find(v =>
                v.lang.startsWith(language)
            );
        }

        // Priority 5: Default English if language not found
        if (!selectedVoice) {
            selectedVoice = voices.find(v => v.lang.startsWith('en'));
        }

        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }

        // Settings for sweet, pleasant voice
        utterance.rate = 0.85;      // Slightly slower for clarity
        utterance.pitch = 1.3;      // Higher pitch for sweetness
        utterance.volume = 0.9;     // Slightly lower to prevent harshness

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
