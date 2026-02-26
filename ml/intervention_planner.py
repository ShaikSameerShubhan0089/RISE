"""
Personalized Intervention Engine
Translates SHAP-based AI insights into localized, practical intervention pathways
for caregivers and AWC workers (Problem B).
"""

from typing import Dict, List, Optional
import pandas as pd

class InterventionPlanner:
    """
    Logic engine to generate individualized intervention pathways based on
    AI risk stratification and SHAP contribution values.
    """
    
    def __init__(self):
        # Language code mapping for robustness
        self.lang_map = {
            'telugu': 'te', 'te': 'te',
            'hindi': 'hi', 'hi': 'hi',
            'kannada': 'kn', 'kn': 'kn',
            'urdu': 'ur', 'ur': 'ur',
            'tamil': 'ta', 'ta': 'ta',
            'english': 'en', 'en': 'en'
        }
        
        # Mapping from features to intervention categories (English keys)
        self.category_mapping = {
            'language_dq': 'Speech Therapy',
            'fine_motor_dq': 'Occupational Therapy',
            'gross_motor_dq': 'Early Intervention',
            'socio_emotional_dq': 'Behavioral Therapy',
            'scii': 'Social Communication Training',
            'behavior_score': 'Behavioral Therapy',
            'nutrition_score': 'Nutritional Support',
            'caregiver_engagement_score': 'Parental Training',
            'stunting': 'Nutritional Support',
            'wasting': 'Nutritional Support',
            'anemia': 'Nutritional Support'
        }

        # Full UI Translation Map
        self.translation_map = {
            'en': {
                'High Risk': 'High Risk', 'Moderate Risk': 'Moderate Risk', 'Low Risk': 'Low Risk', 'Mild Concern': 'Mild Concern',
                'Speech Therapy': 'Speech Therapy', 'Occupational Therapy': 'Occupational Therapy',
                'Early Intervention': 'Early Intervention', 'Behavioral Therapy': 'Behavioral Therapy',
                'Social Communication Training': 'Social Communication Training', 'Nutritional Support': 'Nutritional Support',
                'Parental Training': 'Parental Training',
                'objective': 'Objective', 'daily_steps': 'Daily Steps', 'parent_guide': 'Parent Guide', 'priority': 'Priority',
                'Increases Risk': 'Increases Risk', 'Decreases Risk': 'Decreases Risk',
                'escalation_desc': 'Likelihood of escalating to higher risk based on longitudinal deltas.',
                'impact_of': 'Impact of {feature} on predicted risk',
                # Demographics & Status
                'Male': 'Male', 'Female': 'Female', 'Active': 'Active', 'Inactive': 'Inactive', 'N/A': 'N/A',
                # Improvement Status
                'Significant Improvement': 'Significant Improvement', 'Moderate Improvement': 'Moderate Improvement',
                'In Progress': 'In Progress', 'Decline': 'Decline', 'Stable': 'Stable',
                # Priority
                'High': 'High', 'Moderate': 'Moderate', 'Low': 'Low'
            },
            'te': {
                'High Risk': 'అధిక రిస్క్', 'Moderate Risk': 'మితమైన రిస్క్', 'Low Risk': 'తక్కువ రిస్క్', 'Mild Concern': 'స్వల్ప ఆందోళన',
                'Speech Therapy': 'స్పీచ్ థెరపీ', 'Occupational Therapy': 'ఆక్యుపేషనల్ థెరపీ',
                'Early Intervention': 'ప్రారంభ జోక్యం', 'Behavioral Therapy': 'బిహేవియరల్ థెరపీ',
                'Social Communication Training': 'సామాజిక సంభాషణ శిక్షణ', 'Nutritional Support': 'పోషకాహార మద్దతు',
                'Parental Training': 'తల్లిదండ్రుల శిక్షణ',
                'objective': 'లక్ష్యం', 'daily_steps': 'రోజువారీ దశలు', 'parent_guide': 'తల్లిదండ్రుల గైడ్', 'priority': 'ప్రాధాన్యత',
                'Increases Risk': 'రిస్క్ పెంచుతుంది', 'Decreases Risk': 'రిస్క్ తగ్గిస్తుంది',
                'escalation_desc': 'మునుపటి డేటా ఆధారంగా రిస్క్ పెరిగే అవకాశం ఉంది.',
                'impact_of': 'రిస్క్ మీద {feature} ప్రభావం',
                # Demographics & Status
                'Male': 'పురుషుడు', 'Female': 'స్త్రీ', 'Active': 'క్రియాశీల', 'Inactive': 'నిష్క్రియాత్మక', 'N/A': 'అందుబాటులో లేదు',
                # Improvement Status
                'Significant Improvement': 'గణనీయమైన మెరుగుదల', 'Moderate Improvement': 'ఓ మోస్తారు మెరుగుదల',
                'In Progress': 'కొనసాగుతోంది', 'Decline': 'తగ్గుదల', 'Stable': 'స్థిరంగా ఉంది',
                # Priority
                'High': 'అధికం', 'Moderate': 'మితమైన', 'Low': 'తక్కువ'
            },
            'hi': {
                'High Risk': 'उच्च जोखिम', 'Moderate Risk': 'मध्यम जोखिम', 'Low Risk': 'कम जोखिम', 'Mild Concern': 'मामूली चिंता',
                'Speech Therapy': 'स्पीच थेरेपी', 'Occupational Therapy': 'ऑक्यूपेशनल थेरेपी',
                'Early Intervention': 'प्रारंभिक हस्तक्षेप', 'Behavioral Therapy': 'बिहेवियरल थेरेपी',
                'Social Communication Training': 'सामाजिक संचार प्रशिक्षण', 'Nutritional Support': 'पोषण संबंधी सहायता',
                'Parental Training': 'माता-पिता का प्रशिक्षण',
                'objective': 'उद्देश्य', 'daily_steps': 'दैनिक कदम', 'parent_guide': 'माता-पिता मार्गदर्शिका', 'priority': 'प्राथमिकता',
                'Increases Risk': 'जोखिम बढ़ाता है', 'Decreases Risk': 'जोखिम कम करता है',
                'escalation_desc': 'पिछले डेटा के आधार पर जोखिम बढ़ने की संभावना।',
                'impact_of': 'पूर्वानुमानित जोखिम पर {feature} का प्रभाव',
                # Demographics & Status
                'Male': 'पुरुष', 'Female': 'महिला', 'Active': 'सक्रिय', 'Inactive': 'निष्क्रिय', 'N/A': 'उपलब्ध नहीं',
                # Improvement Status
                'Significant Improvement': 'महत्वपूर्ण सुधार', 'Moderate Improvement': 'मध्यम सुधार',
                'In Progress': 'प्रगति पर है', 'Decline': 'गिरावट', 'Stable': 'स्थिर',
                # Priority
                'High': 'उच्च', 'Moderate': 'मध्यम', 'Low': 'कम'
            },
            'kn': {
                'High Risk': 'ಹೆಚ್ಚಿನ ಅಪಾಯ', 'Moderate Risk': 'ಮಧ್ಯಮ ಅಪಾಯ', 'Low Risk': 'ಕಡಿಮೆ ಅಪಾಯ', 'Mild Concern': 'ಸಣ್ಣ ಕಾಳಜಿ',
                'Speech Therapy': 'ಸ್ಪೀಚ್ ಥೆರಪಿ', 'Occupational Therapy': 'ಆಕ್ಯುಪೇಶನಲ್ ಥೆರಪಿ',
                'Early Intervention': 'ಆರಂಭಿಕ ಹಸ್ತಕ್ಷೇಪ', 'Behavioral Therapy': 'ಬಿಹೇವಿಯರಲ್ ಥೆರಪಿ',
                'Social Communication Training': 'ಸಾಮಾಜಿಕ ಸಂವಹನ ತರಬೇತಿ', 'Nutritional Support': 'ಪೌಷ್ಟಿಕಾಂಶದ ಬೆಂಬಲ',
                'Parental Training': 'ಪೋಷಕರ ತರಬೇತಿ',
                'objective': 'ಉದ್ದೇಶ', 'daily_steps': 'ದೈನಂದಿನ ಹಂತಗಳು', 'parent_guide': 'ಪೋಷಕರ ಮಾರ್ಗದರ್ಶಿ', 'priority': 'ಆದ್ಯತೆ',
                'Increases Risk': 'ಅಪಾಯವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ', 'Decreases Risk': 'ಅಪಾಯವನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ',
                'escalation_desc': 'ಹಳೆಯ ಡೇಟಾ ಆಧಾರದ ಮೇಲೆ ಅಪಾಯ ಹೆಚ್ಚಾಗುವ ಸಾಧ್ಯತೆ.',
                'impact_of': 'ಅಪಾಯದ ಮೇಲೆ {feature} ಪರಿಣಾಮ',
                # Demographics & Status
                'Male': 'ಪುರುಷ', 'Female': 'ಮಹಿಳೆ', 'Active': 'ಸಕ್ರಿಯ', 'Inactive': 'ನಿಷ್ಕ್ರಿಯ', 'N/A': 'ಲಭ್ಯವಿಲ್ಲ',
                # Improvement Status
                'Significant Improvement': 'ಗಣನೀಯ ಸುಧಾರಣೆ', 'Moderate Improvement': 'ಮಧ್ಯಮ ಸುಧಾರಣೆ',
                'In Progress': 'ಪ್ರಗತಿಯಲ್ಲಿದೆ', 'Decline': 'ಕ್ಷೀಣತೆ', 'Stable': 'ಸ್ಥಿರವಾಗಿದೆ',
                # Priority
                'High': 'ಹೆಚ್ಚು', 'Moderate': 'ಮಧ್ಯಮ', 'Low': 'ಕಡಿಮೆ'
            },
            'ur': {
                'High Risk': 'زیادہ خطرہ', 'Moderate Risk': 'درمیانہ خطرہ', 'Low Risk': 'کم خطرہ', 'Mild Concern': 'تھوڑی پریشانی',
                'Speech Therapy': 'اسپیچ تھراپی', 'Occupational Therapy': 'آکیوپیشنل تھراپی',
                'Early Intervention': 'ابتدائی مداخلت', 'Behavioral Therapy': 'بیہیویئرل تھراپی',
                'Social Communication Training': 'سوشل کمیونیکیشن ٹریننگ', 'Nutritional Support': 'غذائی مدد',
                'Parental Training': 'والدین کی تربیت',
                'objective': 'مقصد', 'daily_steps': 'روزانہ کے اقدامات', 'parent_guide': 'والدین کی ہدایت', 'priority': 'ترجیح',
                'Increases Risk': 'خطرہ بڑھاتا ہے', 'Decreases Risk': 'خطرہ کم کرتا ہے',
                'escalation_desc': 'پچھلے ڈیٹا کی بنیاد پر خطرہ بڑھنے کا امکان۔',
                'impact_of': 'خطرہ پر {feature} کا اثر',
                # Demographics & Status
                'Male': 'لڑکا', 'Female': 'لڑکی', 'Active': 'فعال', 'Inactive': 'غیر فعال', 'N/A': 'دستیاب نہیں',
                # Improvement Status
                'Significant Improvement': 'نمایاں بہتری', 'Moderate Improvement': 'اعتدال پسند بہتری',
                'In Progress': 'جاری ہے', 'Decline': 'کمی', 'Stable': 'مستحکم',
                # Priority
                'High': 'زیادہ', 'Moderate': 'درمیانہ', 'Low': 'کم'
            },
            'ta': {
                'High Risk': 'அதிக ஆபத்து', 'Moderate Risk': 'மிதமான ஆபத்து', 'Low Risk': 'குறைந்த ஆபத்து', 'Mild Concern': 'சிறிய கவலை',
                'Speech Therapy': 'பேச்சு சிகிச்சை', 'Occupational Therapy': 'தொழில்சார் சிகிச்சை',
                'Early Intervention': 'ஆரம்பகால தலையீடு', 'Behavioral Therapy': 'நடத்தை சிகிச்சை',
                'Social Communication Training': 'சமூக தொடர்பு பயிற்சி', 'Nutritional Support': 'ஊட்டச்சத்து ஆதரவு',
                'Parental Training': 'பெற்றோர் பயிற்சி',
                'objective': 'குறிக்கோள்', 'daily_steps': 'தினசரி படிகள்', 'parent_guide': 'பெற்றோர் வழிகாட்டி', 'priority': 'முன்னுரிமை',
                'Increases Risk': 'ஆபத்தை அதிகரிக்கிறது', 'Decreases Risk': 'ஆபத்தை குறைக்கிறது',
                'escalation_desc': 'கடந்த கால தரவுகளின் அடிப்படையில் ஆபத்து அதிகரிப்பதற்கான வாய்ப்பு.',
                'impact_of': 'ஆபத்தின் மீது {feature} இன் தாக்கம்',
                # Demographics & Status
                'Male': 'ஆண்', 'Female': 'பெண்', 'Active': 'செயலில்', 'Inactive': 'செயலற்றது', 'N/A': 'கிடைக்கவில்லை',
                # Improvement Status
                'Significant Improvement': 'குறிப்பிடத்தக்க முன்னேற்றம்', 'Moderate Improvement': 'மிதமான முன்னேற்றம்',
                'In Progress': 'செயலில் உள்ளது', 'Decline': 'குறைவு', 'Stable': 'நிலையானது',
                # Priority
                'High': 'அதிகம்', 'Moderate': 'மிதமான', 'Low': 'குறைந்த'
            }
        }

        # Feature name translations
        self.feature_translations = {
            'en': {
                'language_dq': 'Language', 'cognitive_dq': 'Cognitive', 'fine_motor_dq': 'Fine Motor',
                'gross_motor_dq': 'Gross Motor', 'socio_emotional_dq': 'Socio-Emotional',
                'nutrition_score': 'Nutrition', 'caregiver_engagement_score': 'Caregiver Engagement',
                'stimulation_score': 'Stimulation', 'composite_dq': 'Composite Score'
            },
            'te': {
                'language_dq': 'భాష (Language)', 'cognitive_dq': 'జ్ఞానము (Cognitive)', 'fine_motor_dq': 'చేతి నైపుణ్యం (Fine Motor)',
                'gross_motor_dq': 'శారీరక ఎదుగుదల (Gross Motor)', 'socio_emotional_dq': 'సామాజిక ప్రవర్తన',
                'nutrition_score': 'పోషణ', 'caregiver_engagement_score': 'తల్లిదండ్రుల శ్రద్ధ',
                'stimulation_score': 'ప్రేరణ', 'composite_dq': 'మొత్తం స్కోరు'
            },
            'hi': {
                'language_dq': 'भाषा', 'cognitive_dq': 'संज्ञानात्मक', 'fine_motor_dq': 'ठीक मोटर कौशल',
                'gross_motor_dq': 'सकल मोटर कौशल', 'socio_emotional_dq': 'सामाजिक-भावनात्मक',
                'nutrition_score': 'पोषण', 'caregiver_engagement_score': 'देखभाल करने वाले का जुड़ाव',
                'stimulation_score': 'उत्तेजना स्कोर', 'composite_dq': 'समग्र स्कोर'
            },
            'kn': {
                'language_dq': 'ಭಾಷೆ', 'cognitive_dq': 'ಅರಿವು', 'fine_motor_dq': 'ಸೂಕ್ಷ್ಮ ಮೋಟಾರ್',
                'gross_motor_dq': 'ಸ್ಥೂಲ ಮೋಟಾರ್', 'socio_emotional_dq': 'ಸಾಮಾಜಿಕ-ಭಾವನಾತ್ಮಕ',
                'nutrition_score': 'ಪೌಷ್ಟಿಕಾಂಶ', 'caregiver_engagement_score': 'ಪೋಷಕರ ತೊಡಗಿಸಿಕೊಳ್ಳುವಿಕೆ',
                'stimulation_score': 'ಪ್ರಚೋದನೆ', 'composite_dq': 'ಒಟ್ಟಾರೆ ಸ್ಕೋರ್'
            },
            'ur': {
                'language_dq': 'زبان', 'cognitive_dq': 'علمی', 'fine_motor_dq': 'فائن موٹر',
                'gross_motor_dq': 'گراس موٹر', 'socio_emotional_dq': 'سماجی جذباتی',
                'nutrition_score': 'غذائیت', 'caregiver_engagement_score': 'نگہداشت کرنے والے کی شمولیت',
                'stimulation_score': 'حوصلہ افزائی کا اسکور', 'composite_dq': 'مجموعی اسکور'
            },
            'ta': {
                'language_dq': 'மொழி', 'cognitive_dq': 'அறிவாற்றல்', 'fine_motor_dq': 'சிறந்த மோட்டார்',
                'gross_motor_dq': 'பெரிய மோட்டார்', 'socio_emotional_dq': 'சமூக-உணர்ச்சி',
                'nutrition_score': 'ஊட்டச்சத்து', 'caregiver_engagement_score': 'கவனிப்பாளர் ஈடுபாடு',
                'stimulation_score': 'தூண்டுதல் மதிப்பெண்', 'composite_dq': 'ஒட்டுமொத்த மதிப்பெண்'
            }
        }
        
        # Localized content for pathways (Telugu, Hindi, Kannada)
        self.localized_content = {
            'en': {
                'Speech Therapy': {
                    'objective': 'Improve verbal communication and vocabulary.',
                    'daily_steps': [
                        'Spend 10 minutes naming common household objects.',
                        'Read a short story and ask simple questions about it.',
                        'Sing repetitive nursery rhymes together.'
                    ],
                    'parent_guide': 'Speak slowly and clearly. Reward all attempts at verbalization.'
                },
                'Occupational Therapy': {
                    'objective': 'Develop fine motor skills and hand-eye coordination.',
                    'daily_steps': [
                        'Encourage using finger foods for self-feeding.',
                        'Practice stacking blocks or nesting cups.',
                        'Scribble with thick crayons on large paper.'
                    ],
                    'parent_guide': 'Focus on grip strength. Make practice feel like fun play.'
                },
                'Early Intervention': {
                    'objective': 'Build core physical strength and mobility.',
                    'daily_steps': [
                        'Provide "tummy time" or floor play for 15 minutes.',
                        'Help the child pull up to a standing position.',
                        'Encourage crawling towards a favorite toy.'
                    ],
                    'parent_guide': 'Safety first. Ensure a clear, padded area for physical activity.'
                },
                'Behavioral Therapy': {
                    'objective': 'Enhance social engagement and emotional regulation.',
                    'daily_steps': [
                        'Practice making eye contact during feeding or play.',
                        'Use simple gestures like waving "bye-bye".',
                        'Praise positive social interactions immediately.'
                    ],
                    'parent_guide': 'Consistency is key. Use the same positive words for rewards.'
                },
                'Social Communication Training': {
                    'objective': 'Boost joint attention and interactive play.',
                    'daily_steps': [
                        'Play "peek-a-boo" to encourage social anticipation.',
                        'Point to birds or cars and wait for the child to look.',
                        'Practice reciprocal rolling of a ball.'
                    ],
                    'parent_guide': 'Follow the child\'s lead. Engage with what they are interested in.'
                },
                'Nutritional Support': {
                    'objective': 'Ensure optimal physical and brain growth.',
                    'daily_steps': [
                        'Include seasonal fruits and green vegetables in every meal.',
                        'Provide protein-rich foods like pulses or eggs.',
                        'Maintain a fixed schedule for feeding.'
                    ],
                    'parent_guide': 'Avoid junk food. Ensure clean drinking water is always available.'
                },
                'Parental Training': {
                    'objective': 'Empower caregivers with developmental knowledge.',
                    'daily_steps': [
                        'Set a consistent 15-minute "screen-free" play time.',
                        'Describe what you are doing during daily chores (self-talk).',
                        'Maintain a consistent sleep schedule for the child.'
                    ],
                    'parent_guide': 'Mental health matters. Take small breaks for yourself to stay patient.'
                }
            },
            'te': {  # Telugu
                'Speech Therapy': {
                    'objective': 'మాటలు మరియు పదజాలాన్ని మెరుగుపరచడం.',
                    'daily_steps': [
                        'ఇంట్లోని వస్తువుల పేర్లను 10 నిమిషాల పాటు చెప్పండి.',
                        'చిన్న కథను చదివి దాని గురించి ప్రశ్నలు అడగండి.',
                        'పిల్లలతో కలిసి పాటలు లేదా పద్యాలు పాడండి.'
                    ],
                    'parent_guide': 'నెమ్మదిగా మరియు స్పష్టంగా మాట్లాడండి. మాట్లాడటానికి చేసే ప్రయత్నాలను మెచ్చుకోండి.'
                },
                'Occupational Therapy': {
                    'objective': 'చేతి నైపుణ్యాలను మరియు సమన్వయాన్ని పెంచడం.',
                    'daily_steps': [
                        'సొంతంగా తినడం అలవాటు చేయండి.',
                        'బ్లాక్స్ పేర్చడం లేదా కప్పులను అమర్చడం చేయించండి.',
                        'పెద్ద కాగితంపై రంగులతో గీతలు గీయనివ్వండి.'
                    ],
                    'parent_guide': 'పట్టును పెంచడంపై దృష్టి పెట్టండి. దీనిని ఆటగా అనిపించేలా చేయండి.'
                },
                'Early Intervention': {
                    'objective': 'శారీరక బలాన్ని మరియు కదలికలను మెరుగుపరచడం.',
                    'daily_steps': [
                        '15 నిమిషాల పాటు నేలపై బోర్లా పడుకోబెట్టి ఆడించండి.',
                        'పిల్లవాడు పట్టుకుని నిలబడేలా సహాయం చేయండి.',
                        'ఇష్టమైన బొమ్మ వైపు పాకేలా ప్రోత్సహించండి.'
                    ],
                    'parent_guide': 'భద్రత ముఖ్యం. ఆట స్థలం శుభ్రంగా మరియు మెత్తగా ఉండేలా చూడండి.'
                },
                'Behavioral Therapy': {
                    'objective': 'సామాజిక ప్రవర్తన మరియు భావోద్వేగ నియంత్రణను పెంచడం.',
                    'daily_steps': [
                        'ఆహారం ఇచ్చేటప్పుడు కళ్ళలోకి చూడటం అలవాటు చేయండి.',
                        'టాటా (bye-bye) వంటి సైగలు నేర్పండి.',
                        'మంచి ప్రవర్తనను వెంటనే మెచ్చుకోండి.'
                    ],
                    'parent_guide': 'క్రమశిక్షణ ముఖ్యం. బహుమతుల కోసం ఒకే రకమైన మంచి మాటలను వాడండి.'
                },
                'Social Communication Training': {
                    'objective': 'సామాజిక స్పందన మరియు పరస్పర ఆటలను పెంచడం.',
                    'daily_steps': [
                        'దాగుడుమూతలు వంటి సామాజిక ఆటలు ఆడండి.',
                        'బయట పక్షులను లేదా వాహనాలను చూపించి వారినీ చూడమనండి.',
                        'బంతితో ఒకరికొకరు ఆడుకోవడం ప్రాక్టీస్ చేయండి.'
                    ],
                    'parent_guide': 'పిల్లల ఆసక్తిని గమనించండి. వారు ఇష్టపడే వాటితోనే కలిసి ఆడండి.'
                },
                'Nutritional Support': {
                    'objective': 'శారీరక మరియు మెదడు ఎదుగుదలకు తోడ్పడటం.',
                    'daily_steps': [
                        'ప్రతి పూట ఆహారంలో పండ్లు మరియు ఆకుకూరలు ఉండేలా చూడండి.',
                        'పప్పులు లేదా గుడ్లు వంటి ప్రోటీన్ ఆహారాన్ని ఇవ్వండి.',
                        'భోజన సమయాలను ఖచ్చితంగా పాటించండి.'
                    ],
                    'parent_guide': 'జంక్ ఫుడ్ వద్దు. ఎప్పుడూ స్వచ్ఛమైన తాగునీరు అందుబాటులో ఉంచండి.'
                },
                'Parental Training': {
                    'objective': 'పిల్లల ఎదుగుదలపై తల్లిదండ్రులకు అవగాహన కల్పించడం.',
                    'daily_steps': [
                        'ప్రతిరోజూ 15 నిమిషాలు టీవీ/ఫోన్ లేకుండా పిల్లలతో గడపండి.',
                        'మీరు చేసే పనులను పిల్లలకు వివరిస్తూ మాట్లాడండి.',
                        'పిల్లల నిద్ర సమయాలను ఖచ్చితంగా పాటించండి.'
                    ],
                    'parent_guide': 'మీ సహనం ముఖ్యం. మీ మానసిక ఆరోగ్యం కోసం చిన్న విరామాలు తీసుకోండి.'
                }
            },
            'hi': {  # Hindi
                'Speech Therapy': {
                    'objective': 'मौखिक संचार और शब्दावली में सुधार करना।',
                    'daily_steps': [
                        '10 मिनट तक घर की सामान्य वस्तुओं के नाम बताएं।',
                        'एक छोटी कहानी पढ़ें और उसके बारे में सरल प्रश्न पूछें।',
                        'साथ में दोहराव वाली कविताएं गाएं।'
                    ],
                    'parent_guide': 'धीरे-धीरे और स्पष्ट रूप से बोलें। बोलने के सभी प्रयासों को प्रोत्साहित करें।'
                },
                'Occupational Therapy': {
                    'objective': 'ठीक मोटर कौशल और हाथ-आंख समन्वय विकसित करना।',
                    'daily_steps': [
                        'स्वयं भोजन करने के लिए उंगली से खाने वाले खाद्य पदार्थों को बढ़ावा दें।',
                        'ब्लॉक सजाने या कप व्यवस्थित करने का अभ्यास करें।',
                        'बड़े कागज़ पर मोटे क्रेयॉन से चित्र बनाएं।'
                    ],
                    'parent_guide': 'पकड़ की मजबूती पर ध्यान दें। अभ्यास को मजेदार खेल जैसा बनाएं।'
                },
                'Early Intervention': {
                    'objective': 'शारीरिक शक्ति और गतिशीलता का निर्माण करना।',
                    'daily_steps': [
                        '15 मिनट के लिए फर्श पर पेट के बल खेलने का समय दें।',
                        'बच्चे को खड़े होने की स्थिति में आने में मदद करें।',
                        'पसंदीदा खिलौने की ओर रेंगने के लिए प्रोत्साहित करें।'
                    ],
                    'parent_guide': 'सुरक्षा पहले। शारीरिक गतिविधि के लिए एक साफ और गद्देदार क्षेत्र सुनिश्चित करें।'
                },
                'Behavioral Therapy': {
                    'objective': 'सामाजिक जुड़ाव और भावनात्मक विनियमन को बढ़ाना।',
                    'daily_steps': [
                        'खिलाते या खेलते समय आंखों में आंखें डालने का अभ्यास करें।',
                        'सरल इशारों जैसे "बाय-बाय" का उपयोग करें।',
                        'सकारात्मक सामाजिक व्यवहार की तुरंत प्रशंसा करें।'
                    ],
                    'parent_guide': 'निरंतरता महत्वपूर्ण है। पुरस्कारों के लिए समान सकारात्मक शब्दों का उपयोग करें।'
                },
                'Social Communication Training': {
                    'objective': 'संयुक्त ध्यान और संवादात्मक खेल को बढ़ावा देना।',
                    'daily_steps': [
                        'सामाजिक प्रत्याशा को प्रोत्साहित करने के लिए "पीक-ए-बू" खेलें।',
                        'पक्षियों या कारों की ओर इशारा करें और बच्चे के देखने का इंतजार करें।',
                        'साथ में गेंद के साथ खेलने का अभ्यास करें।'
                    ],
                    'parent_guide': 'बच्चे की रुचि का अनुसरण करें। जिसमें उनकी रुचि हो, उसमें शामिल हों।'
                },
                'Nutritional Support': {
                    'objective': 'इष्टतम शारीरिक और मस्तिष्क विकास सुनिश्चित करना।',
                    'daily_steps': [
                        'हर भोजन में मौसमी फल और हरी सब्जियां शामिल करें।',
                        'दालें या अंडे जैसे प्रोटीन युक्त खाद्य पदार्थ प्रदान करें।',
                        'भोजन के लिए एक निश्चित समय सारणी बनाए रखें।'
                    ],
                    'parent_guide': 'जंक फूड से बचें। हमेशा साफ पीने का पानी उपलब्ध रखें।'
                },
                'Parental Training': {
                    'objective': 'देखभाल करने वालों को विकासात्मक ज्ञान के साथ सशक्त बनाना।',
                    'daily_steps': [
                        '15 मिनट का "स्क्रीन-फ्री" खेलने का समय निर्धारित करें।',
                        'दैनिक कार्यों के दौरान आप जो कर रहे हैं उसका वर्णन करें।',
                        'बच्चे के सोने का एक निश्चित समय निर्धारित करें।'
                    ],
                    'parent_guide': 'मानसिक स्वास्थ्य मायने रखता है। धैर्य बनाए रखने के लिए छोटे ब्रेक लें।'
                }
            },
            'kn': {  # Kannada
                'Speech Therapy': {
                    'objective': 'ಸಂವಹನ ಮತ್ತು ಶಬ್ದಕೋಶವನ್ನು ಸುಧಾರಿಸುವುದು.',
                    'daily_steps': [
                        '10 ನಿಮಿಷಗಳ ಕಾಲ ಮನೆಯ ಸಾಮಾನ್ಯ ವಸ್ತುಗಳ ಹೆಸರನ್ನು ಹೇಳಿಕೊಡಿ.',
                        'ಸಣ್ಣ ಕಥೆಯನ್ನು ಓದಿ ಅದರ ಬಗ್ಗೆ ಸರಳ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಿ.',
                        'ಒಟ್ಟಾಗಿ ಪುನರಾವರ್ತಿತ ಪದ್ಯಗಳನ್ನು ಹಾಡಿ.'
                    ],
                    'parent_guide': 'ನಿಧಾನವಾಗಿ ಮತ್ತು ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ. ಮಾತಾಡುವ ಅವರ ಪ್ರಯತ್ನಗಳನ್ನು ಪ್ರೋತ್ಸಾಹಿಸಿ.'
                },
                'Occupational Therapy': {
                    'objective': 'ಸೂಕ್ಷ್ಮ ಮೋಟಾರ್ ಕೌಶಲಗಳು ಮತ್ತು ಸಮನ್ವಯತೆಯನ್ನು ಅಭಿವೃದ್ಧಿಪಡಿಸುವುದು.',
                    'daily_steps': [
                        'ಸ್ವತಃ ತಿನ್ನಲು ಬೆರಳಿನ ಆಹಾರಗಳನ್ನು (finger foods) ನೀಡಿ.',
                        'ಬ್ಲಾಕ್‌ಗಳನ್ನು ಜೋಡಿಸುವ ಅಭ್ಯಾಸ ಮಾಡಿಸಿ.',
                        'ದೊಡ್ಡ ಕಾಗದದ ಮೇಲೆ ಕ್ರಯಾನ್‌ಗಳಿಂದ ಚಿತ್ರಗಳನ್ನು ಬಿಡಿಸಲು ಬಿಡಿ.'
                    ],
                    'parent_guide': 'ಹಿಡಿತದ ಸಾಮರ್ಥ್ಯದ ಮೇಲೆ ಗಮನ ಹರಿಸಿ. ಇದನ್ನು ಆಟದಂತೆ ಮೋಜಿನಿಂದ ಮಾಡಿಸಿ.'
                },
                'Early Intervention': {
                    'objective': 'ದೈಹಿಕ ಸಾಮರ್ಥ್ಯ ಮತ್ತು ಚಲನೆಯನ್ನು ವೃದ್ಧಿಸುವುದು.',
                    'daily_steps': [
                        '15 ನಿಮಿಷಗಳ ಕಾಲ ಮಗುವನ್ನು ಹೊಟ್ಟೆಯ ಮೇಲೆ ಮಲಗಿಸಿ ಆಡಿಸಿ.',
                        'ಮಗು ಎದ್ದು ನಿಲ್ಲಲು ಸಹಾಯ ಮಾಡಿ.',
                        'ಇಷ್ಟದ ಆಟಿಕೆಗಳ ಕಡೆಗೆ ಅಂಬೆಗಾಲು ಇಡಲು ಪ್ರೋತ್ಸಾಹಿಸಿ.'
                    ],
                    'parent_guide': 'ಸುರಕ್ಷತೆ ಮುಖ್ಯ. ದೈಹಿಕ ಚಟುವಟಿಕೆಗಾಗಿ ಸರಿಯಾದ ಸ್ಥಳವನ್ನು ಒದಗಿಸಿ.'
                },
                'Behavioral Therapy': {
                    'objective': 'ಸಾಮಾಜಿಕ ತೊಡಗಿಸಿಕೊಳ್ಳುವಿಕೆ ಮತ್ತು ಭಾವನಾತ್ಮಕ ನಿಯಂತ್ರಣವನ್ನು ಹೆಚ್ಚಿಸುವುದು.',
                    'daily_steps': [
                        'ಆಹಾರ ನೀಡುವಾಗ ಅಥವಾ ಆಟವಾಡುವಾಗ ಕಣ್ಣಲ್ಲಿ ಕಣ್ಣಿಟ್ಟು ನೋಡುವುದನ್ನು ರೂಢಿಸಿ.',
                        '"ಬೈ-ಬೈ" ಎನ್ನುವಂತಹ ಸಣ್ಣ ಸನ್ನೆಗಳನ್ನು ಬಳಸಿ.',
                        'ಉತ್ತಮ ಸಾಮಾಜಿಕ ನಡವಳಿಕೆಯನ್ನು ತಕ್ಷಣವೇ ಮೆಚ್ಚಿ.'
                    ],
                    'parent_guide': 'ಶಿಸ್ತು ಮತ್ತು ಸತತ ಪ್ರಯತ್ನ ಮುಖ್ಯ. ಪ್ರತಿಫಲ ನೀಡಲು ಒಂದೇ ರೀತಿಯ ಪದಗಳನ್ನು ಬಳಸಿ.'
                },
                'Social Communication Training': {
                    'objective': 'ಜಂಟಿ ಗಮನ ಮತ್ತು ಸಂವಹನದ ಆಟಗಳನ್ನು ವೃದ್ಧಿಸುವುದು.',
                    'daily_steps': [
                        'ಸಾಮಾಜಿಕ ಸಂವಹನಕ್ಕಾಗಿ "ಪೀಕ್-ಎ-ಬೂ" ನಂತಹ ಆಟವಾಡಿ.',
                        'ಹಕ್ಕಿಗಳು ಅಥವಾ ಕಾರುಗಳನ್ನು ತೋರಿಸಿ ಮಗುವಿಗೆ ಗಮನಿಸಲು ಹೇಳಿ.',
                        'ಪರಸ್ಪರ ಚೆಂಡನ್ನು ಉರುಳಿಸುವ ಆಟಗಳನ್ನು ಆಡಿ.'
                    ],
                    'parent_guide': 'ಮಗುವಿನ ಆಸಕ್ತಿಯನ್ನು ಗಮನಿಸಿ. ಅವರು ಇಷ್ಟಪಡುವ ವಿಷಯಗಳಲ್ಲಿ ತೊಡಗಿಸಿಕೊಳ್ಳಿ.'
                },
                'Nutritional Support': {
                    'objective': 'ದೈಹಿಕ ಮತ್ತು ಮೆದುಳಿನ ಬೆಳವಣಿಗೆಯನ್ನು ಖಚಿತಪಡಿಸುವುದು.',
                    'daily_steps': [
                        'ಪ್ರತಿ ಊಟದಲ್ಲಿ ಕಾಲೋಚಿತ ಹಣ್ಣುಗಳು ಮತ್ತು ಹಸಿರು ತರಕಾರಿಗಳನ್ನು ಸೇರಿಸಿ.',
                        'ಬೇಳೆಕಾಳುಗಳು ಅಥವಾ ಮೊಟ್ಟೆಗಳಂತಹ ಪ್ರೋಟೀನ್ ಆಹಾರಗಳನ್ನು ನೀಡಿ.',
                        'ಊಟಕ್ಕೆ ನಿಗದಿತ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಅನುಸರಿಸಿ.'
                    ],
                    'parent_guide': 'ಜಂಕ್ ಫುಡ್ ಬೇಡ. ಮಗುವಿಗೆ ಯಾವಾಗಲೂ ಶುದ್ಧ ಕುಡಿಯುವ ನೀರು ಲಭ್ಯವಿರುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ.'
                },
                'Parental Training': {
                    'objective': 'ಮಕ್ಕಳ ಬೆಳವಣಿಗೆಯ ಬಗ್ಗೆ ಪೋಷಕರಿಗೆ ಅರಿವು ಮೂಡಿಸುವುದು.',
                    'daily_steps': [
                        'ಪ್ರತಿದಿನ 15 ನಿಮಿಷ "ಟಿವಿ/ಫೋನ್" ಇಲ್ಲದೆ ಮಗುವಿನೊಂದಿಗೆ ಕಳೆಯಿರಿ.',
                        'ದೈನಂದಿನ ಕೆಲಸಗಳ ಸಮಯದಲ್ಲಿ ನೀವು ಮಾಡುತ್ತಿರುವುದನ್ನು ಮಗುವಿಗೆ ವಿವರಿಸಿ.',
                        'ಮಗುವಿನ ನಿದ್ರೆಯ ವೇಳಾಪಟ್ಟಿಯನ್ನು ಸರಿಯಾಗಿ ಪಾಲಿಸಿ.'
                    ],
                    'parent_guide': 'ನಿಮ್ಮ ಮಾನಸಿಕ ಆರೋಗ್ಯ ಮುಖ್ಯ. ತಾಳ್ಮೆಯಿಂದ ಇರಲು ಸಣ್ಣ ವಿರಾಮಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.'
                }
            },
            'ur': {  # Urdu
                'Speech Therapy': {
                    'objective': 'زبانی رابطے اور ذخیرہ الفاظ کو بہتر بنائیں۔',
                    'daily_steps': [
                        'گھر کی عام ایشیاء کے نام بتانے میں 10 منٹ گزاریں۔',
                        'ایک چھوٹی کہانی پڑھیں اور اس کے بارے میں آسان سوالات پوچھیں۔',
                        'ایک ساتھ دہرائی جانے والی نظمیں گائیں۔'
                    ],
                    'parent_guide': 'آہستہ اور واضح بولیں۔ بولنے کی تمام کوششوں کا صلہ دیں۔'
                },
                'Occupational Therapy': {
                    'objective': 'فائن موٹر مہارتوں اور ہاتھ اور آنکھ کے ہم آہنگی کو فروغ دیں۔',
                    'daily_steps': [
                        'خود کھانے کے لیے انگلیوں کے کھانے کے استعمال کی حوصلہ افزائی کریں۔',
                        'بلاک لگانے یا کپ رکھنے کی مشق کریں۔',
                        'بڑے کاغذ پر موٹی رنگین پنسلوں سے لکھیں۔'
                    ],
                    'parent_guide': 'پکڑ کی مضبوطی پر توجہ دیں۔ مشق کو تفریحی کھیل کی طرح محسوس کرائیں۔'
                },
                'Early Intervention': {
                    'objective': 'بنیادی جسمانی طاقت اور نقل و حرکت بنائیں۔',
                    'daily_steps': [
                        '15 منٹ تک پیٹ کے بل لیٹنے یا فرش پر کھیلنے کا وقت دیں۔',
                        'بچے کو کھڑے ہونے کی پوزیشن میں آنے میں مدد کریں۔',
                        'پسندیدہ کھلونے کی طرف رینگنے کی حوصلہ افزائی کریں۔'
                    ],
                    'parent_guide': 'پہلے حفاظت۔ جسمانی سرگرمی کے لیے صاف اور گدی دار جگہ کو یقینی بنائیں۔'
                },
                'Behavioral Therapy': {
                    'objective': 'سماجی شمولیت اور جذباتی ضابطے کو بہتر بنائیں۔',
                    'daily_steps': [
                        'کھانے یا کھیلنے کے دوران آنکھوں سے رابطہ کرنے کی مشق کریں۔',
                        'خدا حافظ (bye-bye) جیسے سادہ اشارے استعمال کریں۔',
                        'مثبت سماجی تعامل کی فوری تعریف کریں۔'
                    ],
                    'parent_guide': 'مستقلی ضروری ہے۔ انعامات کے لیے ایک جیسے مثبت الفاظ استعمال کریں۔'
                },
                'Social Communication Training': {
                    'objective': 'باہمی توجہ اور انٹرایکٹو کھیل کو فروغ دیں۔',
                    'daily_steps': [
                        'سماجی توقع کی حوصلہ افزائی کے لیے "چھپن چھپائی" (peek-a-boo) کھیلیں۔',
                        'پرندوں یا گاڑیوں کی طرف اشارہ کریں اور بچے کے دیکھنے کا انتظار کریں۔',
                        'ایک دوسرے کی طرف گیند رول کرنے کی مشق کریں۔'
                    ],
                    'parent_guide': 'بچے کی رہنمائی پر عمل کریں۔ اس میں شامل ہوں جس میں ان کی دلچسپی ہو۔'
                },
                'Nutritional Support': {
                    'objective': 'بہترین جسمانی اور دماغی نشوونما کو یقینی بنائیں۔',
                    'daily_steps': [
                        'ہر کھانے میں موسمی پھل اور ہری سبزیاں شامل کریں۔',
                        'دالیں یا انڈے جیسی پروٹین سے بھرپور غذائیں فراہم کریں۔',
                        'کھانے کے لیے ایک مقررہ وقت کا شیڈول بنائیں۔'
                    ],
                    'parent_guide': 'غیر صحت بخش کھانے سے پرہیز کریں۔ یقینی بنائیں کہ پینے کا صاف پانی ہمیشہ دستیاب ہے۔'
                },
                'Parental Training': {
                    'objective': 'نگہداشت کرنے والوں کو ترقیاتی علم سے بااختیار بنائیں۔',
                    'daily_steps': [
                        'ایک مستقل 15 منٹ "اسکرین سے پاک" کھیلنے کا وقت مقرر کریں۔',
                        'روزانہ کے کاموں کے دوران آپ جو کر رہے ہیں اس کی وضاحت کریں (اپنے آپ سے بات کریں)۔',
                        'بچے کے لیے نیند کا ایک مستقل شیڈول بنائیں۔'
                    ],
                    'parent_guide': 'ذہنی صحت اہمیت رکھتی ہے۔ صبر برقرار رکھنے کے لیے اپنے لیے چھوٹے وقفے لیں۔'
                }
            },
            'ta': {  # Tamil
                'Speech Therapy': {
                    'objective': 'வாய்மொழி தொடர்பு மற்றும் சொல்லகராதியை மேம்படுத்தவும்.',
                    'daily_steps': [
                        'பொதுவான வீட்டுப் பொருட்களின் பெயர்களைக் கூற 10 நிமிடங்கள் செலவிடுங்கள்.',
                        'ஒரு சிறுகதையைப் படித்து அதைப் பற்றி எளிய கேள்விகளைக் கேளுங்கள்.',
                        'ஒரே மாதிரியான நர்சரி ரைம்ஸை ஒன்றாகப் பாடுங்கள்.'
                    ],
                    'parent_guide': 'மெதுவாகவும் தெளிவாகவும் பேசுங்கள். பேச்சு முயற்சியைப் பாராட்டுங்கள்.'
                },
                'Occupational Therapy': {
                    'objective': 'சிறந்த மோட்டார் திறன்கள் மற்றும் கண்-கை ஒருங்கிணைப்பை வளர்த்துக் கொள்ளுங்கள்.',
                    'daily_steps': [
                        'சுயமாக உண்பதற்கு விரல் உணவுகளைப் பயன்படுத்த ஊக்குவிக்கவும்.',
                        'பிளாக்குகளை அடுக்குவது அல்லது கப்களைப் பொருத்துவது போன்றவற்றை பயிற்சி செய்யவும்.',
                        'பெரிய காகிதத்தில் தடிமனான மெழுகுவண்ண பென்சில்களால் வரையச் சொல்லுங்கள்.'
                    ],
                    'parent_guide': 'பிடியின் வலிமையில் கவனம் செலுத்துங்கள். பயிற்சியை வேடிக்கையாக மாற்றவும்.'
                },
                'Early Intervention': {
                    'objective': 'அடிப்படை உடல் வலிமை மற்றும் இயக்கத்தை உருவாக்குங்கள்.',
                    'daily_steps': [
                        '15 நிமிடங்கள் தரையில் விளையாட அல்லது குப்புறப் படுக்கச் செய்யுங்கள்.',
                        'குழந்தையை நிற்க உதவும் நிலைக்கு வர உதவுங்கள்.',
                        'பிடித்த பொம்மையை நோக்கி தவழ ஊக்குவியுங்கள்.'
                    ],
                    'parent_guide': 'பாதுகாப்பு முதலில். உடல் செயல்பாட்டிற்கு சுத்தமான மற்றும் பாதுகாப்பான இடத்தை உறுதி செய்யுங்கள்.'
                },
                'Behavioral Therapy': {
                    'objective': 'சமூக ஈடுபாடு மற்றும் உணர்ச்சி ஒழுங்குமுறையை மேம்படுத்தவும்.',
                    'daily_steps': [
                        'உணவு உண்ணும் போது அல்லது விளையாடும் போது கண்களைப் பார்த்து பேசுங்கள்.',
                        'டாட்டா (bye-bye) போன்ற எளிய சைகைகளைப் பயன்படுத்துங்கள்.',
                        'நேர்மறையான சமூக தொடர்பை உடனடியாகப் பாராட்டுங்கள்.'
                    ],
                    'parent_guide': 'தொடர்ச்சி முக்கியம். பாராட்டுகளுக்கு ஒரே மாதிரியான நேர்மறைச் சொற்களைப் பயன்படுத்துங்கள்.'
                },
                'Social Communication Training': {
                    'objective': 'கவனம் மற்றும் ஊடாடும் விளையாட்டை அதிகரிக்கவும்.',
                    'daily_steps': [
                        'சமூக எதிர்பார்ப்பை ஊக்குவிக்க "பிகப்பு" (peek-a-boo) விளையாடுங்கள்.',
                        'பறவைகள் அல்லது கார்களைச் சுட்டிக்காட்டி குழந்தையை பார்க்கச் சொல்லுங்கள்.',
                        'பந்தைத் தள்ளு விளையாட்டைப் பயிற்சி செய்யுங்கள்.'
                    ],
                    'parent_guide': 'குழந்தையின் விருப்பத்தைப் பின்பற்றுங்கள். அவர்கள் எதில் ஆர்வமாக இருக்கிறார்கள் என்பதில் ஈடுபடுங்கள்.'
                },
                'Nutritional Support': {
                    'objective': 'சிறந்த உடல் மற்றும் மூளை வளர்ச்சியை உறுதி செய்யவும்.',
                    'daily_steps': [
                        'ஒவ்வொரு உணவிலும் பருவகால பழங்கள் மற்றும் பச்சை காய்கறிகளைச் சேர்க்கவும்.',
                        'பருப்பு அல்லது முட்டை போன்ற புரதம் நிறைந்த உணவுகளை வழங்கவும்.',
                        'உணவு உண்பதற்கான நிலையான நேரத்தைப் பின்பற்றுங்கள்.'
                    ],
                    'parent_guide': 'ஜங்க் உணவுகளைத் தவிர்க்கவும். சுத்தமான குடிநீர் எப்போதும் கிடைப்பதை உறுதி செய்யவும்.'
                },
                'Parental Training': {
                    'objective': 'வளர்ச்சி பற்றிய அறிவைக் கொண்டு கவனிப்பாளர்களுக்கு அதிகாரம் அளிக்கவும்.',
                    'daily_steps': [
                        'தினமும் 15 நிமிடங்கள் போன்/டிவி இல்லாத விளையாட்டு நேரத்தை ஒதுக்குங்கள்.',
                        'தினசரி வேலைகளின் போது நீங்கள் என்ன செய்கிறீர்கள் என்பதை விவரிக்கவும்.',
                        'குழந்தைக்கு நிலையான தூக்க நேரத்தைப் பின்பற்றுங்கள்.'
                    ],
                    'parent_guide': 'மனநலம் முக்கியம். பொறுமையாக இருக்க உங்களுக்காகச் சிறிய இடைவேளைகளை எடுத்துக் கொள்ளுங்கள்.'
                }
            }
        }

    def generate_pathway(self, shap_explanations: List[Dict], lang: str = 'en') -> List[Dict]:
        """
        Generate a prioritized list of intervention recommendations based on SHAP impacts.
        
        Args:
            shap_explanations: List of dicts with 'feature_name' and 'shap_value'
            lang: Language code ('en', 'te', 'hi')
        """
        recommendations = []
        
        # Sort by SHAP value (most impactful first) 
        # Focus on features that INCREASE risk (positive SHAP)
        sorted_features = sorted(
            [f for f in shap_explanations if f['shap_value'] > 0],
            key=lambda x: x['shap_value'],
            reverse=True
        )
        
        target_lang = self.lang_map.get(lang.lower(), 'en')
        content = self.localized_content.get(target_lang, self.localized_content['en'])
        uimap = self.translation_map.get(target_lang, self.translation_map['en'])
        
        seen_categories = set()
        for feature in sorted_features:
            feature_name = feature['feature_name']
            category = self.category_mapping.get(feature_name)
            
            if category and category not in seen_categories:
                category_content = content.get(category, {})
                
                recommendations.append({
                    'category': uimap.get(category, category),
                    'priority': uimap.get('High' if len(recommendations) < 2 else 'Moderate'),
                    'objective': category_content.get('objective', 'Support growth.'),
                    'daily_steps': category_content.get('daily_steps', []),
                    'parent_guide': category_content.get('parent_guide', 'Consult expert.'),
                    'ui_labels': {
                        'objective': uimap['objective'],
                        'daily_steps': uimap['daily_steps'],
                        'parent_guide': uimap['parent_guide'],
                        'priority_label': uimap['priority']
                    },
                    'triggered_by': feature_name,
                    'impact_score': round(feature['shap_value'], 4)
                })
                seen_categories.add(category)
        
        # If no specific features triggered, add general Parental Training
        if not recommendations:
            cat_content = content['Parental Training']
            recommendations.append({
                'category': 'Parental Training',
                'priority': 'Low',
                'objective': cat_content.get('objective'),
                'daily_steps': cat_content.get('daily_steps'),
                'parent_guide': cat_content.get('parent_guide'),
                'triggered_by': 'General Assessment',
                'impact_score': 0.0
            })
            
        return recommendations

    def get_clinical_summary(self, risk_tier: str, probability: float, lang: str = 'en') -> str:
        """Generate a concise clinical summary for the caregiver."""
        target_lang = self.lang_map.get(lang.lower(), 'en')
        uimap = self.translation_map.get(target_lang, self.translation_map['en'])
        
        # Translate risk tier itself
        localized_tier = uimap.get(risk_tier, risk_tier)
        
        summaries = {
            'en': f"Risk Assessment: {localized_tier} ({probability*100:.1f}% confidence). Primary intervention focus identified below.",
            'te': f"రిస్క్ అసెస్మెంట్: {localized_tier} ({probability*100:.1f}% ఖచ్చితత్వం). ప్రాథమిక జోక్యం అవసరం కింది విధంగా గుర్తించబడింది.",
            'hi': f"जोखिम मूल्यांकन: {localized_tier} ({probability*100:.1f}% निश्चितता)। प्राथमिक हस्तक्षेप की आवश्यकता नीचे दी गई है।",
            'kn': f"ಜೋಖಮು ಮೌಲ್ಯಮಾಪನ: {localized_tier} ({probability*100:.1f}% ಖಚಿತತೆ). ಪ್ರಾಥಮಿಕ ಹಸ್ತಕ್ಷೇಪದ ಅಗತ್ಯವನ್ನು ಕೆಳಗೆ ಗುರುತಿಸಲಾಗಿದೆ.",
            'ur': f"رسک اسسمنٹ: {localized_tier} ({probability*100:.1f}% یقین). بنیادی مداخلت کی ضرورت ذیل میں دی گئی ہے۔",
            'ta': f"ஆபத்து மதிப்பீடு: {localized_tier} ({probability*100:.1f}% உறுதி). முதன்மை தலையீடு தேவை கீழே கொடுக்கப்பட்டுள்ளது."
        }
        return summaries.get(target_lang, summaries['en'])

    def localize_prediction(self, prediction: Dict, lang: str = 'en') -> Dict:
        """Deep-translates a prediction object for localized UI display."""
        target_lang = self.lang_map.get(lang.lower(), 'en')
        uimap = self.translation_map.get(target_lang, self.translation_map['en'])
        featmap = self.feature_translations.get(target_lang, self.feature_translations['en'])
        
        if not prediction:
            return prediction
            
        # 1. Localize Risk Tier
        prediction['risk_tier'] = uimap.get(prediction['risk_tier'], prediction['risk_tier'])
        
        # 2. Localize SHAP Explanations
        if 'top_features' in prediction:
            for feat in prediction['top_features']:
                fname = feat.get('feature_name', '')
                localized_fname = featmap.get(fname, fname.replace('_', ' ').title())
                
                # Localize Interpretation
                feat['interpretation'] = uimap.get('impact_of', 'Impact of {feature}').format(feature=localized_fname)
                
                # Localize Direction
                feat['impact_direction'] = uimap.get(feat.get('impact_direction'), feat.get('impact_direction'))
        
        # 3. Localize Escalation
        prediction['escalation_description'] = uimap.get('escalation_desc', 'Likelihood of escalating risk.')
        
        return prediction

    def localize_value(self, value: Optional[str], lang: str = 'en') -> str:
        """Localize a single categorical value (e.g. 'Male', 'Active')."""
        if not value:
            return ""
        target_lang = self.lang_map.get(lang.lower(), 'en')
        uimap = self.translation_map.get(target_lang, self.translation_map['en'])
        return uimap.get(value, value)

    def localize_item(self, item: Dict, keys: List[str], lang: str = 'en') -> Dict:
        """Localize specific keys within a dictionary."""
        for key in keys:
            if key in item and isinstance(item[key], str):
                item[key] = self.localize_value(item[key], lang)
        return item
