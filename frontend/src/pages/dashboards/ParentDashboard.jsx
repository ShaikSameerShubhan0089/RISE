import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { dashboardAPI } from '../../utils/api';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';

/* ── colour helpers ──────────────────────────────────────────────────────── */
const RISK_COLORS = {
    'Low Risk': '#22c55e',
    'Mild Concern': '#f59e0b',
    'Moderate Risk': '#f97316',
    'High Risk': '#ef4444',
    'No Assessment': '#94a3b8',
};
const DQ_LINES = [
    { key: 'composite_dq', label: 'Composite', color: '#7c3aed' },
    { key: 'gross_motor_dq', label: 'Gross Motor', color: '#2563eb' },
    { key: 'fine_motor_dq', label: 'Fine Motor', color: '#059669' },
    { key: 'language_dq', label: 'Language', color: '#d97706' },
    { key: 'cognitive_dq', label: 'Cognitive', color: '#dc2626' },
    { key: 'socio_emotional_dq', label: 'Socio-Emo.', color: '#db2777' },
];

/* ── flag badge ──────────────────────────────────────────────────────────── */
const FlagBadge = ({ val, trueLabel, falseLabel, language = 'en' }) => {
    const ui = UI_TEXT[language] || UI_TEXT.en;
    const tLab = trueLabel || ui.yes;
    const fLab = falseLabel || ui.no;
    if (val === null || val === undefined) return <span className="text-gray-300">—</span>;
    return (
        <span className={`px-1.5 py-0.5 rounded text-xs font-medium ${val ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
            {val ? tLab : fLab}
        </span>
    );
};

/* ── DQ score cell ──────────────────────────────────────────────────────── */
const DQCell = ({ v }) => {
    if (v == null) return <span className="text-gray-300">—</span>;
    const cls = v < 70 ? 'text-red-600 font-bold' : v < 85 ? 'text-amber-600 font-semibold' : 'text-gray-800';
    return <span className={cls}>{v.toFixed(1)}</span>;
};

/* ── CSV helper ─────────────────────────────────────────────────────────── */
const exportCSV = (filename, rows) => {
    if (!rows.length) return;
    const headers = Object.keys(rows[0]);
    const body = [headers, ...rows.map(r => headers.map(h => r[h] ?? ''))].map(r => r.join(',')).join('\n');
    const blob = new Blob([body], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = filename; a.click();
    URL.revokeObjectURL(url);
};

/* ══════════════════════════════════════════════════════════════════════════ */
/* ── UI Text Map ────────────────────────────────────────────────────────── */
const UI_TEXT = {
    en: {
        hero: 'Hello', sub: 'Track your child\'s progress at the Anganwadi centre',
        tabs: ['Overview', 'AI Insights', 'Growth', 'Health', 'Screening', 'Plans'],
        warning: 'Important: This system provides progress tracking only. For medical concerns, please consult a qualified paediatrician.',
        title: 'Individualized Intervention Pathway',
        summary_title: 'Early Warning Summary',
        risk_tier_label: 'Tier',
        escalation_label: 'Risk Escalation Probability (Early Warning)',
        basis: 'Basis', ai_weight: 'AI Weight', goal: 'Next Steps & Goal',
        health_title: 'Health Records', screening_title: 'Developmental Screening', plans_title: 'Intervention Plans',
        export_csv: 'Export CSV',
        headers: {
            health: ['Cycle', 'Date', 'Age', 'Comp DQ', 'Delayed', 'Nutrition', 'Stunting', 'Wasting', 'Anemia'],
            screening: ['Cycle', 'Date', 'Age', 'Autism Screen', 'ADHD Risk', 'Behavior Risk', 'Attention', 'Behavior', 'Stimulation'],
            summary: ['Total Assessments', 'Latest DQ', 'Autism Screen +ve', 'ADHD Risk']
        },
        viewing: 'Viewing:', risk_dist: 'Risk Distribution — All Children', no_insights: 'No AI insights available',
        dob: 'DOB', gender: 'Gender', centre: 'Centre', caregiver: 'Caregiver', status: 'Status',
        sessions: 'Sessions', ongoing: 'Ongoing', compliance: 'compliance', provider: 'Provider',
        yes: 'Yes', no: 'No', flagged: 'Flagged', clear: 'Clear', at_risk: 'At Risk',
        no_records: 'No records found.', priority_label: 'Priority',
        goal_desc: "Based on {name}'s current parameters, we aim to improve {feature} through consistent practice as outlined above. Progress will be reviewed in the next assessment cycle.",
        dq_labels: {
            composite_dq: 'Composite', gross_motor_dq: 'Gross Motor', fine_motor_dq: 'Fine Motor',
            language_dq: 'Language', cognitive_dq: 'Cognitive', socio_emotional_dq: 'Socio-Emo.'
        }
    },
    te: {
        hero: 'నమస్కారం', sub: 'అంగన్‌వాడీ కేంద్రంలో మీ పిల్లల పురోగతిని ట్రాక్ చేయండి',
        tabs: ['అవలోకనం', 'AI అంతర్దృష్టులు', 'ఎదుగుదల', 'ఆరోగ్యం', 'స్క్రీనింగ్', 'ప్లాన్‌లు'],
        warning: 'ముఖ్య గమనిక: ఈ సిస్టమ్ పురోగతి ట్రాకింగ్‌ను మాత్రమే అందిస్తుంది. వైద్య సంబంధిత ఆందోళనల కోసం, దయచేసి అర్హత కలిగిన శిశువైద్యుడిని సంప్రదించండి.',
        title: 'వ్యక్తిగత జోక్య మార్గం',
        summary_title: 'ముందస్తు హెచ్చరిక సారాంశం',
        risk_tier_label: 'రిస్క్ స్థాయి',
        escalation_label: 'రిస్క్ పెరిగే అవకాశం (ముందస్తు హెచ్చరిక)',
        basis: 'ఆధారం', ai_weight: 'AI బరువు', goal: 'తదుపరి దశలు & లక్ష్యం',
        health_title: 'ఆరోగ్య రికార్డులు', screening_title: 'డెవలప్‌మెంటల్ స్క్రీనింగ్', plans_title: 'జోక్య ప్రణాళಿಕలు',
        export_csv: 'CSV డౌన్‌లోడ్',
        headers: {
            health: ['చక్రం', 'తేదీ', 'వయస్సు', 'DQ స్కోరు', 'ఆలస్యం', 'పోషణ', 'స్టంటింగ్', 'వేస్టింగ్', 'రక్తహీనత'],
            screening: ['చక్రం', 'తేదీ', 'వయస్సు', 'ఆటిజం స్క్రీన్', 'ADHD రిస్క్', 'ప్రవర్తన రిస్క్', 'ఏకాగ్రత', 'ప్రవర్తన', 'ప్రేరణ'],
            summary: ['మొత్తం తనిఖీలు', 'తాజా DQ', 'ఆటిజం పాజిటివ్', 'ADHD రిಸ್క్']
        },
        viewing: 'చూస్తున్నారు:', risk_dist: 'రిస్క్ పంపిణీ — పిల్లలందరూ', no_insights: 'AI అంతర్దృష్టులు అందుబాటులో లేవు',
        dob: 'పుట్టిన తేదీ', gender: 'లింగం', centre: 'కేంద్రం', caregiver: 'సంరక్షకుడు', status: 'స్థితి',
        sessions: 'సెషన్లు', ongoing: 'కొనసాగుతోంది', compliance: 'అనుసరణ', provider: 'ప్రదాత',
        yes: 'అవును', no: 'కాదు', flagged: 'ఫ్లాగ్ చేయబడింది', clear: 'స్పష్టం', at_risk: 'రిస్క్ లో ఉంది',
        no_records: 'రికార్డులు ఏవీ లేవు.',
        goal_desc: "{name} యొక్క ప్రస్తుత నిలకడల ఆధారంగా, పైన పేర్కొన్న విధంగా స్థిరమైన అభ్యాసం ద్వారా {feature}ను మెరుగుపరచడమే మా లక్ష్యం. తదుపరి తనిఖీ చక్రంలో పురోగతి సమీక్షించబడుతుంది.",
        dq_labels: {
            composite_dq: 'మొత్తం (Composite)', gross_motor_dq: 'శారీరక (Gross Motor)', fine_motor_dq: 'చేతి (Fine Motor)',
            language_dq: 'భాష (Language)', cognitive_dq: 'జ్ఞానము (Cognitive)', socio_emotional_dq: 'సామాజిక (Socio-Emo.)'
        }
    },
    hi: {
        hero: 'नमस्ते', sub: 'आंगनवाड़ी केंद्र में अपने बच्चे की प्रगति पर नज़र रखें',
        tabs: ['अवलोकन', 'AI अंतर्दृष्टि', 'विकास', 'स्वास्थ्य', 'स्क्रीनिंग', 'योजनाएं'],
        warning: 'महत्वपूर्ण: यह प्रणाली केवल प्रगति ट्रैकिंग प्रदान करती है। चिकित्सा संबंधी चिंताओं के लिए, कृपया एक योग्य बाल रोग विशेषज्ञ से परामर्श करें।',
        title: 'व्यक्तिगत हस्तक्षेप पथ',
        summary_title: 'प्रारंभिक चेतावनी सारांश',
        risk_tier_label: 'जोखिम स्तर',
        escalation_label: 'जोखिम बढ़ने की संभावना (प्रारंभिक चेतावनी)',
        basis: 'आधार', ai_weight: 'AI वजन', goal: 'अगले कदम और लक्ष्य',
        health_title: 'स्वास्थ्य रिकॉर्ड', screening_title: 'विकासात्मक स्क्रीनिंग', plans_title: 'हस्तक्षेप योजनाएं',
        export_csv: 'CSV निर्यात',
        headers: {
            health: ['चक्र', 'दिनांक', 'आयु', 'DQ स्कोर', 'विलंब', 'पोषण', 'स्टंटिंग', 'वेस्टिंग', 'एनीमिया'],
            screening: ['चक्र', 'दिनांक', 'आयु', 'ऑटिज्म स्क्रीन', 'ADHD जोखिम', 'व्यवहार जोखिम', 'ध्यान', 'व्यवहार', 'उत्तेजना'],
            summary: ['कुल मूल्यांकन', 'नवीनतम DQ', 'ऑटिज्म स्क्रीन +ve', 'ADHD जोखिम']
        },
        viewing: 'देख रहे हैं:', risk_dist: 'जोखिम वितरण — सभी बच्चे', no_insights: 'AI अंतर्दृष्टि उपलब्ध नहीं है',
        dob: 'जन्म तिथि', gender: 'लिंग', centre: 'केंद्र', caregiver: 'देखभाल करने वाला', status: 'स्थिति',
        sessions: 'सत्र', ongoing: 'चल रहा है', compliance: 'अनुपालन', provider: 'प्रदाता',
        yes: 'हां', no: 'नहीं', flagged: 'चिह्नित', clear: 'स्पष्ट', at_risk: 'जोखिम में',
        no_records: 'कोई रिकॉर्ड नहीं मिला।',
        goal_desc: "{name} के वर्तमान मापदंडों के आधार पर, हमारा लक्ष्य ऊपर बताए अनुसार निरंतर अभ्यास के माध्यम से {feature} में सुधार करना है। प्रगति की समीक्षा अगले मूल्यांकन चक्र में की जाएगी।",
        dq_labels: {
            composite_dq: 'समग्र (Composite)', gross_motor_dq: 'सकल मोटर (Gross)', fine_motor_dq: 'ठीक मोटर (Fine)',
            language_dq: 'भाषा (Language)', cognitive_dq: 'संज्ञानात्मक (Cognitive)', socio_emotional_dq: 'सामाजिक (Socio-Emo.)'
        }
    },
    kn: {
        hero: 'ನಮಸ್ಕಾರ', sub: 'ಅಂಗನವಾಡಿ ಕೇಂದ್ರದಲ್ಲಿ ನಿಮ್ಮ ಮಗುವಿನ ಪ್ರಗತಿಯನ್ನು ಗಮನಿಸಿ',
        tabs: ['ಅವಲೋಕನ', 'AI ಒಳನೋಟಗಳು', 'ಬೆಳವಣಿಗೆ', 'ಆರೋಗ್ಯ', 'ಸ್ಕ್ರೀನಿಂಗ್', 'ಯೋಜನೆಗಳು'],
        warning: 'ಪ್ರಮುಖ ಸೂಚನೆ: ಈ ವ್ಯವಸ್ಥೆಯು ಕೇವಲ ಪ್ರಗತಿಯ ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸುತ್ತದೆ. ವೈದ್ಯಕೀಯ ಸಮಸ್ಯೆಗಳಿಗಾಗಿ, ದಯವಿಟ್ಟು ತಜ್ಞ ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.',
        title: 'ವೈಯಕ್ತಿಕ ಹಸ್ತಕ್ಷೇಪ ಮಾರ್ಗ',
        summary_title: 'ಮುನ್ನೆಚ್ಚರಿಕೆ ಸಾರಾಂಶ',
        risk_tier_label: 'ಅಪಾಯದ ಮಟ್ಟ',
        escalation_label: 'ಅಪಾಯ ಹೆಚ್ಚಾಗುವ ಸಾಧ್ಯತೆ (ಮುನ್ನೆಚ್ಚರಿಕೆ)',
        basis: 'ಆಧಾರ', ai_weight: 'AI ತೂಕ', goal: 'ಮುಂದಿನ ಹಂತಗಳು ಮತ್ತು ಗುರಿ',
        health_title: 'ಆರೋಗ್ಯ ದಾಖಲೆಗಳು', screening_title: 'ಅಭಿವೃದ್ಧಿ ಸ್ಕ್ರೀನಿಂಗ್', plans_title: 'ಹಸ್ತಕ್ಷೇಪ ಯೋಜನೆಗಳು',
        export_csv: 'CSV ರಫ್ತು',
        headers: {
            health: ['ಸುತ್ತು', 'ದಿನಾಂಕ', 'ವಯಸ್ಸು', 'DQ ಸ್ಕೋರ್', 'ವಿಳಂಬ', 'ಪೌಷ್ಟಿಕಾಂಶ', 'ಕುಂಠಿತ', 'ವೇಸ್ಟಿಂಗ್', 'ರಕ್ತಹೀನತೆ'],
            screening: ['ಸುತ್ತು', 'ದಿನಾಂಕ', 'ವಯಸ್ಸು', 'ಆಟಿಸಂ ಸ್ಕ್ರೀನ್', 'ADHD ಅಪಾಯ', 'ವರ್ತನೆ ಅಪಾಯ', 'ಗಮನ', 'ವರ್ತನೆ', 'ಪ್ರಚೋದನೆ'],
            summary: ['ಒಟ್ಟು ಮೌಲ್ಯಮಾಪನ', 'ಇತ್ತೀಚಿನ DQ', 'ಆಟಿಸಂ ಧನಾತ್ಮಕ', 'ADHD ಅಪಾಯ']
        },
        viewing: 'ವೀಕ್ಷಣೆ:', risk_dist: 'ಅಪಾಯ ವಿತರಣೆ — ಎಲ್ಲಾ ಮಕ್ಕಳು', no_insights: 'ಯಾವುದೇ AI ಒಳನೋಟಗಳು ಲಭ್ಯವಿಲ್ಲ',
        dob: 'ಹುಟ್ಟಿದ ದಿನಾಂಕ', gender: 'ಲಿಂಗ', centre: 'ಕೇಂದ್ರ', caregiver: 'ಪೋಷಕರು', status: 'ಸ್ಥಿತಿ',
        sessions: 'ಸೆಷನ್‌ಗಳು', ongoing: 'ಪ್ರಗತಿಯಲ್ಲಿದೆ', compliance: 'ಅನುಸರಣೆ', provider: 'ಒದಗಿಸುವವರು',
        yes: 'ಹೌದು', no: 'ಇಲ್ಲ', flagged: 'ಗುರುತಿಸಲಾಗಿದೆ', clear: 'ಸ್ಪಷ್ಟವಾಗಿದೆ', at_risk: 'ಅಪಾಯದಲ್ಲಿದೆ',
        no_records: 'ಯಾವುದೇ ದಾಖಲೆಗಳು ಕಂಡುಬಂದಿಲ್ಲ.',
        goal_desc: "{name} ರ ಪ್ರಸ್ತುತ ನಿಯತಾಂಕಗಳ ಆಧಾರದ ಮೇಲೆ, ಮೇಲೆ ವಿವರಿಸಿದಂತೆ ಸ್ಥಿರವಾದ ಅಭ್ಯಾಸದ ಮೂಲಕ {feature} ಅನ್ನು ಸುಧಾರಿಸುವ ಗುರಿಯನ್ನು ನಾವು ಹೊಂದಿದ್ದೇವೆ. ಮುಂದಿನ ಮೌಲ್ಯಮಾಪನ ಚಕ್ರದಲ್ಲಿ ಪ್ರಗತಿಯನ್ನು ಪರಿಶೀಲಿಸಲಾಗುತ್ತದೆ.",
        dq_labels: {
            composite_dq: 'ಒಟ್ಟಾರೆ (Composite)', gross_motor_dq: 'ಸ್ಥೂಲ ಮೋಟಾರ್ (Gross)', fine_motor_dq: 'ಸೂಕ್ಷ್ಮ ಮೋಟಾರ್ (Fine)',
            language_dq: 'ಭಾಷೆ (Language)', cognitive_dq: 'ಅರಿವು (Cognitive)', socio_emotional_dq: 'ಸಾಮಾಜಿಕ (Socio-Emo.)'
        }
    }
};

/* ══════════════════════════════════════════════════════════════════════════ */
const ParentDashboard = () => {
    const { user } = useAuth();

    const [children, setChildren] = useState([]);
    const [interventions, setInterventions] = useState([]);
    const [selectedChild, setSelectedChild] = useState(null);
    const [growthData, setGrowthData] = useState(null);
    const [growthLoading, setGrowthLoading] = useState(false);
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState('overview');
    const [language, setLanguage] = useState('en');

    const ui = UI_TEXT[language] || UI_TEXT.en;

    /* ── Boot ──────────────────────────────────────────────────────────── */
    useEffect(() => {
        Promise.all([
            dashboardAPI.getChildren(),
            dashboardAPI.getInterventions(),
        ]).then(([c, i]) => {
            const kids = c.data || [];
            setChildren(kids);
            setInterventions(i.data || []);
            if (kids.length) setSelectedChild(kids[0]);
        }).catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    /* ── Load growth on child change ────────────────────────────────── */
    useEffect(() => {
        if (!selectedChild) return;
        setGrowthData(null);
        setGrowthLoading(true);
        dashboardAPI.getChildGrowth(selectedChild.child_id, language)
            .then(r => setGrowthData(r.data))
            .catch(() => setGrowthData({ error: true }))
            .finally(() => setGrowthLoading(false));
    }, [selectedChild, language]);

    /* ── Derived data ───────────────────────────────────────────────── */
    const riskPieData = (() => {
        const counts = {};
        children.forEach(ch => {
            const risk = ch.risk_tier || 'No Assessment';
            counts[risk] = (counts[risk] || 0) + 1;
        });
        return Object.entries(counts).map(([name, value]) => ({ name, value }));
    })();

    const datapoints = growthData?.datapoints || [];

    const childInterventions = interventions.filter(i =>
        selectedChild && i.child_name === `${selectedChild.first_name} ${selectedChild.last_name || ''}`.trim()
    );

    if (loading) return (
        <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-purple-600" />
        </div>
    );

    const tabs = [
        { id: 'overview', label: `🏠 ${ui.tabs[0]}` },
        { id: 'insights', label: `🤖 ${ui.tabs[1]}` },
        { id: 'growth', label: `📈 ${ui.tabs[2]}` },
        { id: 'health', label: `🩺 ${ui.tabs[3]}` },
        { id: 'vaccination', label: `💉 ${ui.tabs[4]}` },
        { id: 'interventions', label: `🏥 ${ui.tabs[5]}` },
    ];

    return (
        <div className="p-6 space-y-6 max-w-6xl mx-auto">

            {/* Hero */}
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-6 text-white shadow-lg">
                <h1 className="text-2xl font-bold">{ui.hero}, {user?.full_name}! 👋</h1>
                <p className="text-purple-100 mt-1 text-sm">{ui.sub}</p>
            </div>

            {/* Child selector (multi-child parent) */}
            {children.length > 1 && (
                <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm flex flex-wrap gap-3 items-center">
                    <span className="text-sm font-semibold text-gray-600">{ui.viewing}</span>
                    {children.map(ch => (
                        <button
                            key={ch.child_id}
                            onClick={() => setSelectedChild(ch)}
                            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${selectedChild?.child_id === ch.child_id
                                ? 'bg-purple-600 text-white shadow'
                                : 'bg-gray-100 text-gray-700 hover:bg-purple-50'
                                }`}
                        >
                            {ch.first_name} {ch.last_name || ''}
                        </button>
                    ))}
                </div>
            )}

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="flex gap-1 flex-wrap">
                    {tabs.map(t => (
                        <button
                            key={t.id}
                            onClick={() => setTab(t.id)}
                            className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors ${tab === t.id ? 'bg-purple-600 text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                                }`}
                        >
                            {t.label}
                        </button>
                    ))}
                </nav>
            </div>

            {/* ── OVERVIEW ─────────────────────────────────────────────────── */}
            {tab === 'overview' && (
                <div className="space-y-6">
                    {/* Child info cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {children.map(child => (
                            <div
                                key={child.child_id}
                                onClick={() => setSelectedChild(child)}
                                className={`bg-white rounded-xl border-2 p-5 shadow-sm cursor-pointer transition-all ${selectedChild?.child_id === child.child_id
                                    ? 'border-purple-400 ring-1 ring-purple-200'
                                    : 'border-gray-200 hover:border-purple-200'
                                    }`}
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div>
                                        <p className="font-semibold text-gray-900 text-lg">{child.first_name} {child.last_name}</p>
                                        <p className="text-xs text-gray-400 font-mono mt-0.5">{child.unique_child_code}</p>
                                    </div>
                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${child.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                                        }`}>{child.status}</span>
                                </div>
                                <div className="space-y-1 text-sm text-gray-600">
                                    <div>🎂 {ui.dob}: {child.dob}</div>
                                    <div>👤 {ui.gender}: {child.gender}</div>
                                    <div>🏫 {ui.centre}: {child.center_name}</div>
                                    <div>📱 {ui.caregiver}: {child.caregiver_name} {child.caregiver_phone ? `· ${child.caregiver_phone}` : ''}</div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Risk pie (multi-child only) */}
                    {children.length > 1 && riskPieData.length > 0 && (
                        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                            <h3 className="text-base font-semibold text-gray-800 mb-4">{ui.risk_dist}</h3>
                            <ResponsiveContainer width="100%" height={220}>
                                <PieChart>
                                    <Pie data={riskPieData} cx="50%" cy="50%" outerRadius={85} dataKey="value"
                                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                                        {riskPieData.map((e, i) => <Cell key={i} fill={RISK_COLORS[e.name] || '#94a3b8'} />)}
                                    </Pie>
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </div>
            )}

            {/* ── AI INSIGHTS & PATHWAYS ───────────────────────────────────── */}
            {tab === 'insights' && (
                <div className="space-y-6">
                    {/* Language Selector */}
                    <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-gray-200 shadow-sm transition-all hover:shadow-md">
                        <h3 className="font-semibold text-gray-800">{ui.title}</h3>
                        <div className="flex gap-2">
                            {[
                                { id: 'en', label: 'English' },
                                { id: 'te', label: 'తెలుగు' },
                                { id: 'hi', label: 'हिन्दी' },
                                { id: 'kn', label: 'ಕನ್ನಡ' }
                            ].map(l => (
                                <button
                                    key={l.id}
                                    onClick={() => setLanguage(l.id)}
                                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${language === l.id
                                        ? 'bg-purple-600 text-white shadow-sm'
                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                                >
                                    {l.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {growthLoading ? (
                        <div className="flex items-center justify-center h-48">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" />
                        </div>
                    ) : !growthData?.latest_prediction ? (
                        <div className="bg-white rounded-xl border border-gray-200 p-10 text-center text-gray-400">
                            {ui.no_insights} — {selectedChild?.first_name}
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Left: Summary & Early Warning */}
                            <div className="lg:col-span-1 space-y-6">
                                <div className={`p-5 rounded-xl border-2 shadow-sm ${growthData.latest_prediction.probability > 0.6
                                    ? 'bg-red-50 border-red-200'
                                    : 'bg-green-50 border-green-200'
                                    }`}>
                                    <h4 className="font-bold text-gray-900 mb-2">{ui.summary_title}</h4>
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className={`p-2 rounded-lg ${growthData.latest_prediction.probability > 0.6 ? 'bg-red-200' : 'bg-green-200'
                                            }`}>
                                            <span className="text-xl">⚠️</span>
                                        </div>
                                        <div>
                                            <p className="text-xs text-gray-500 uppercase font-bold text-[10px]">{ui.risk_tier_label}</p>
                                            <p className={`text-lg font-black ${growthData.latest_prediction.probability > 0.6 ? 'text-red-700' : 'text-green-700'
                                                }`}>{growthData.latest_prediction.risk_tier}</p>
                                        </div>
                                    </div>

                                    {growthData.latest_prediction.escalation_probability !== null && (
                                        <div className="mt-4 p-3 bg-white rounded-lg border border-gray-100">
                                            <p className="text-xs font-semibold text-gray-500 mb-1">{ui.escalation_label}</p>
                                            <div className="flex items-center gap-2">
                                                <div className="flex-1 bg-gray-100 h-2 rounded-full overflow-hidden">
                                                    <div className="h-full bg-orange-500" style={{ width: `${growthData.latest_prediction.escalation_probability * 100}%` }} />
                                                </div>
                                                <span className="text-xs font-bold text-orange-700">{(growthData.latest_prediction.escalation_probability * 100).toFixed(0)}%</span>
                                            </div>
                                            <p className="text-[10px] text-gray-400 mt-1 italic leading-tight">
                                                {growthData.latest_prediction.escalation_description || "AI Prediction: Likelihood of escalating risk."}
                                            </p>
                                        </div>
                                    )}
                                </div>

                                <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                                    <h4 className="font-bold text-gray-800 mb-3 text-sm">{ui.tabs[1]}</h4>
                                    <p className="text-xs text-gray-600 leading-relaxed mb-4 p-3 bg-purple-50 rounded-lg border border-purple-100 italic">
                                        "{growthData.latest_prediction.clinical_summary}"
                                    </p>
                                    <div className="space-y-2">
                                        {growthData.latest_prediction.top_features?.map((f, i) => (
                                            <div key={i} className="flex items-center justify-between text-[11px] p-2 bg-gray-50 rounded border border-gray-100">
                                                <span className="text-gray-700 font-medium">{f.interpretation} ({f.impact_direction})</span>
                                                <span className={`font-bold ${f.shap_value > 0 ? 'text-red-500' : 'text-green-500'}`}>
                                                    {f.shap_value > 0 ? '↑' : '↓'}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Right: Individualized Pathway */}
                            <div className="lg:col-span-2 space-y-4">
                                <h4 className="font-bold text-gray-800 flex items-center gap-2">
                                    <span className="p-1 bg-purple-100 rounded text-purple-700">🎯</span>
                                    {ui.title}
                                </h4>
                                <div className="space-y-4">
                                    {growthData.latest_prediction.recommendations?.map((rec, i) => (
                                        <div key={i} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm relative overflow-hidden group hover:border-purple-300 transition-all hover:shadow-md">
                                            <div className={`absolute top-0 left-0 w-1 h-full ${rec.priority === 'High' ? 'bg-red-500' : rec.priority === 'Moderate' ? 'bg-orange-500' : 'bg-green-500'
                                                }`} />
                                            <div className="flex justify-between items-start mb-2">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xl">{
                                                        rec.category.includes('Speech') ? '🗣️' :
                                                            rec.category.includes('Motor') ? '💪' :
                                                                rec.category.includes('Nutrition') ? '🥗' :
                                                                    rec.category.includes('Behavioral') ? '🧠' : '👨‍👩‍👧'
                                                    }</span>
                                                    <h5 className="font-bold text-gray-900">{rec.category}</h5>
                                                </div>
                                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${rec.priority === 'High' || rec.priority === 'అధికం' || rec.priority === 'उच्च' || rec.priority === 'ಹೆಚ್ಚು' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                                                    }`}>{rec.priority}</span>
                                            </div>
                                            <div className="space-y-3">
                                                {/* Objective */}
                                                <div>
                                                    <p className="text-[10px] uppercase font-black text-purple-400 tracking-wider">{rec.ui_labels?.objective || 'Objective'}</p>
                                                    <p className="text-sm text-gray-900 font-medium">{rec.objective}</p>
                                                </div>

                                                {/* Daily Steps */}
                                                {rec.daily_steps && rec.daily_steps.length > 0 && (
                                                    <div>
                                                        <p className="text-[10px] uppercase font-black text-purple-400 tracking-wider">{rec.ui_labels?.daily_steps || 'Daily Steps'}</p>
                                                        <ul className="mt-1 space-y-1">
                                                            {rec.daily_steps.map((step, idx) => (
                                                                <li key={idx} className="text-xs text-gray-700 flex items-start gap-2">
                                                                    <span className="text-purple-400">•</span>
                                                                    <span>{step}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}

                                                {/* Parent Guide */}
                                                <div className="bg-purple-50 p-3 rounded-lg border border-purple-100">
                                                    <p className="text-[10px] uppercase font-black text-purple-500 tracking-wider">{rec.ui_labels?.parent_guide || 'Parent Guide'}</p>
                                                    <p className="text-xs text-purple-800 italic mt-0.5">"{rec.parent_guide}"</p>
                                                </div>
                                            </div>
                                            <div className="mt-4 pt-3 border-t border-gray-50 flex items-center gap-3">
                                                <div className="flex items-center gap-1">
                                                    <span className="text-[10px] text-gray-400 uppercase font-bold">{ui.basis}:</span>
                                                    <span className="text-[10px] font-mono text-gray-500">{rec.triggered_by}</span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <span className="text-[10px] text-gray-400 uppercase font-bold">{ui.ai_weight}:</span>
                                                    <span className="text-[10px] font-mono text-gray-500">{(rec.impact_score * 100).toFixed(1)}%</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                <div className="bg-gradient-to-br from-indigo-50 to-purple-100 p-5 rounded-xl border border-indigo-200">
                                    <h5 className="font-bold text-indigo-900 text-sm mb-2 flex items-center gap-2">
                                        <span>🏁</span> {ui.goal}
                                    </h5>
                                    <p className="text-sm text-indigo-800 italic leading-relaxed">
                                        {ui.goal_desc
                                            .replace('{name}', selectedChild?.first_name || '')
                                            .replace('{feature}', (growthData.latest_prediction.top_features?.[0]?.interpretation || '').split('(')[0].trim() || '—')}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* ── GROWTH CHART ─────────────────────────────────────────────── */}
            {tab === 'growth' && (
                <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-4">
                    {growthLoading ? (
                        <div className="flex items-center justify-center h-48">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" />
                        </div>
                    ) : !datapoints.length ? (
                        <p className="text-center text-gray-400 py-10">{ui.no_records} — {selectedChild?.first_name}</p>
                    ) : (
                        <>
                            <div className="flex items-center justify-between flex-wrap gap-2">
                                <h3 className="font-semibold text-gray-800">{ui.tabs[2]} Trend — {growthData?.child_name}</h3>
                                <button
                                    onClick={() => exportCSV(`growth_${growthData?.unique_child_code}.csv`,
                                        datapoints.map(d => ({
                                            Cycle: d.cycle, Date: d.assessment_date, 'Age(mo)': d.age_months,
                                            'Composite DQ': d.composite_dq, 'Gross Motor': d.gross_motor_dq,
                                            'Fine Motor': d.fine_motor_dq, Language: d.language_dq,
                                            Cognitive: d.cognitive_dq, 'Socio-Emotional': d.socio_emotional_dq,
                                        }))
                                    )}
                                    className="text-xs px-3 py-1.5 bg-purple-50 text-purple-700 border border-purple-200 rounded-lg hover:bg-purple-100"
                                >
                                    {ui.export_csv}
                                </button>
                            </div>

                            {/* DQ summary mini-cards */}
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                                {DQ_LINES.map(({ key, color }) => {
                                    const pts = datapoints.filter(d => d[key] != null);
                                    if (!pts.length) return null;
                                    const latest = pts[pts.length - 1][key];
                                    const delta = latest - pts[0][key];
                                    const label = ui.dq_labels?.[key] || key;
                                    return (
                                        <div key={key} className="rounded-lg p-3 text-center" style={{ background: color + '15', border: `1px solid ${color}30` }}>
                                            <p className="text-xs mb-1" style={{ color }}>{label}</p>
                                            <p className="text-xl font-bold" style={{ color }}>{latest.toFixed(1)}</p>
                                            <p className={`text-xs mt-0.5 font-medium ${delta >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                                                {delta >= 0 ? '↑' : '↓'} {Math.abs(delta).toFixed(1)}
                                            </p>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Line chart */}
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={datapoints} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                                    <XAxis dataKey="cycle" tick={{ fontSize: 11 }}
                                        label={{ value: 'Assessment Cycle', position: 'insideBottom', offset: -2 }} />
                                    <YAxis domain={[0, 120]} tick={{ fontSize: 11 }}
                                        label={{ value: 'DQ Score', angle: -90, position: 'insideLeft' }} />
                                    <Tooltip />
                                    <Legend />
                                    {DQ_LINES.map(({ key, color }) => (
                                        <Line key={key} type="monotone" dataKey={key} stroke={color} name={ui.dq_labels?.[key] || key}
                                            strokeWidth={2} dot={{ r: 3 }} connectNulls />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </>
                    )}
                </div>
            )}

            {/* ── HEALTH RECORDS ───────────────────────────────────────────── */}
            {tab === 'health' && (
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="font-semibold text-gray-800">{ui.health_title} — {selectedChild?.first_name}</h3>
                        {datapoints.length > 0 && (
                            <button
                                onClick={() => exportCSV(`health_${growthData?.unique_child_code}.csv`,
                                    datapoints.map(d => ({
                                        Cycle: d.cycle, Date: d.assessment_date, 'Age(mo)': d.age_months,
                                        'Composite DQ': d.composite_dq, 'Delayed Domains': d.delayed_domains,
                                        'Nutrition Score': d.nutrition_score,
                                        'Stunting': d.stunting ? 'Yes' : 'No',
                                        'Wasting': d.wasting ? 'Yes' : 'No',
                                        'Anemia': d.anemia ? 'Yes' : 'No',
                                        'Attention Score': d.attention_score,
                                        'Behavior Score': d.behavior_score,
                                    }))
                                )}
                                className="text-xs px-3 py-1.5 bg-purple-50 text-purple-700 border border-purple-200 rounded-lg hover:bg-purple-100"
                            >
                                ↓ Export CSV
                            </button>
                        )}
                    </div>

                    {growthLoading ? (
                        <div className="flex items-center justify-center h-32">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" />
                        </div>
                    ) : !datapoints.length ? (
                        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">No records found.</div>
                    ) : (
                        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-50 text-xs text-gray-500 uppercase border-b border-gray-200">
                                    <tr>
                                        {ui.headers.health.map(h => (
                                            <th key={h} className="px-3 py-3 text-left font-semibold whitespace-nowrap">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                    {[...datapoints].reverse().map(d => (
                                        <tr key={d.cycle} className="hover:bg-gray-50">
                                            <td className="px-3 py-3 font-mono text-xs text-gray-500">{d.cycle}</td>
                                            <td className="px-3 py-3 whitespace-nowrap">{d.assessment_date || '—'}</td>
                                            <td className="px-3 py-3">{d.age_months != null ? `${d.age_months} mo` : '—'}</td>
                                            <td className="px-3 py-3"><DQCell v={d.composite_dq} /></td>
                                            <td className="px-3 py-3">
                                                <span className={`font-medium ${d.delayed_domains > 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                                    {d.delayed_domains ?? '—'}
                                                </span>
                                            </td>
                                            <td className="px-3 py-3">
                                                {d.nutrition_score != null
                                                    ? <span className={d.nutrition_score < 60 ? 'text-red-600 font-medium' : 'text-gray-700'}>{d.nutrition_score.toFixed(1)}</span>
                                                    : '—'}
                                            </td>
                                            <td className="px-3 py-3"><FlagBadge val={d.stunting} language={language} /></td>
                                            <td className="px-3 py-3"><FlagBadge val={d.wasting} language={language} /></td>
                                            <td className="px-3 py-3"><FlagBadge val={d.anemia} language={language} /></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* ── SCREENING / VACCINATION ──────────────────────────────────── */}
            {tab === 'vaccination' && (
                <div className="space-y-4">
                    <h3 className="font-semibold text-gray-800">{ui.screening_title} — {selectedChild?.first_name}</h3>

                    {growthLoading ? (
                        <div className="flex items-center justify-center h-32">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" />
                        </div>
                    ) : !datapoints.length ? (
                        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">No screening data yet.</div>
                    ) : (
                        <div className="space-y-4">
                            {/* Attendance / cycle completion info */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                {ui.headers.summary.map((label, idx) => {
                                    const values = [
                                        datapoints.length,
                                        datapoints[datapoints.length - 1]?.composite_dq?.toFixed(1) ?? '—',
                                        datapoints.filter(d => d.autism_screen_flag).length,
                                        datapoints.filter(d => d.adhd_risk).length
                                    ];
                                    const colors = ['text-purple-600', 'text-blue-600', 'text-red-600', 'text-orange-600'];
                                    return (
                                        <div key={label} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm text-center">
                                            <p className={`text-xl font-bold ${colors[idx]}`}>{values[idx]}</p>
                                            <p className="text-xs text-gray-500 mt-1">{label}</p>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Screening table */}
                            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead className="bg-gray-50 text-xs text-gray-500 uppercase border-b border-gray-200">
                                        <tr>
                                            {ui.headers.screening.map(h => (
                                                <th key={h} className="px-3 py-3 text-left font-semibold whitespace-nowrap">{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {[...datapoints].reverse().map(d => (
                                            <tr key={d.cycle} className="hover:bg-gray-50">
                                                <td className="px-3 py-3 font-mono text-xs text-gray-500">{d.cycle}</td>
                                                <td className="px-3 py-3 whitespace-nowrap">{d.assessment_date || '—'}</td>
                                                <td className="px-3 py-3">{d.age_months != null ? `${d.age_months} mo` : '—'}</td>
                                                <td className="px-3 py-3"><FlagBadge val={d.autism_screen_flag} trueLabel={`⚠️ ${ui.flagged}`} falseLabel={`✅ ${ui.clear}`} language={language} /></td>
                                                <td className="px-3 py-3"><FlagBadge val={d.adhd_risk} trueLabel={`⚠️ ${ui.at_risk}`} falseLabel={`✅ ${ui.clear}`} language={language} /></td>
                                                <td className="px-3 py-3"><FlagBadge val={d.behavior_risk} trueLabel={`⚠️ ${ui.at_risk}`} falseLabel={`✅ ${ui.clear}`} language={language} /></td>
                                                <td className="px-3 py-3 text-gray-700">{d.attention_score?.toFixed(1) ?? '—'}</td>
                                                <td className="px-3 py-3 text-gray-700">{d.behavior_score?.toFixed(1) ?? '—'}</td>
                                                <td className="px-3 py-3 text-gray-700">{d.stimulation_score?.toFixed(1) ?? '—'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            {/* Latest screening summary card */}
                            {(() => {
                                const latest = datapoints[datapoints.length - 1];
                                return (
                                    <div className="bg-purple-50 border border-purple-200 rounded-xl p-5">
                                        <h4 className="font-semibold text-purple-900 mb-3">
                                            Latest Screening (Cycle {latest.cycle})
                                        </h4>
                                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                                            <div>
                                                <p className="text-purple-600 text-xs font-medium mb-1">Autism Screen</p>
                                                <FlagBadge val={latest.autism_screen_flag} trueLabel={`⚠️ ${ui.flagged}`} falseLabel={`✅ ${ui.clear}`} language={language} />
                                            </div>
                                            <div>
                                                <p className="text-purple-600 text-xs font-medium mb-1">ADHD Risk</p>
                                                <FlagBadge val={latest.adhd_risk} trueLabel={`⚠️ ${ui.at_risk}`} falseLabel={`✅ ${ui.clear}`} language={language} />
                                            </div>
                                            <div>
                                                <p className="text-purple-600 text-xs font-medium mb-1">Behaviour Risk</p>
                                                <FlagBadge val={latest.behavior_risk} trueLabel={`⚠️ ${ui.at_risk}`} falseLabel={`✅ ${ui.clear}`} language={language} />
                                            </div>
                                            <div>
                                                <p className="text-purple-600 text-xs font-medium mb-1">Attention Score</p>
                                                <span className="font-semibold text-gray-800">{latest.attention_score?.toFixed(1) ?? '—'} / 100</span>
                                            </div>
                                            <div>
                                                <p className="text-purple-600 text-xs font-medium mb-1">Stimulation Score</p>
                                                <span className="font-semibold text-gray-800">{latest.stimulation_score?.toFixed(1) ?? '—'} / 100</span>
                                            </div>
                                            <div>
                                                <p className="text-purple-600 text-xs font-medium mb-1">Delayed Domains</p>
                                                <span className={`font-semibold ${latest.delayed_domains > 0 ? 'text-red-700' : 'text-green-700'}`}>
                                                    {latest.delayed_domains ?? '—'} / 5
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })()}
                        </div>
                    )}
                </div>
            )}

            {/* ── INTERVENTIONS ─────────────────────────────────────────────── */}
            {tab === 'interventions' && (
                <div className="space-y-3">
                    {!childInterventions.length ? (
                        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
                            No interventions on record for {selectedChild?.first_name}.
                        </div>
                    ) : childInterventions.map(i => (
                        <div key={i.intervention_id} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
                            <div className="flex items-start justify-between mb-2">
                                <div>
                                    <p className="font-medium text-gray-900">{i.intervention_type}</p>
                                    <p className="text-xs text-gray-500 mt-0.5">{i.intervention_category}</p>
                                </div>
                                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${i.improvement_status === 'Significant Improvement' ? 'bg-green-100 text-green-800' :
                                    i.improvement_status === 'Moderate Improvement' ? 'bg-teal-100 text-teal-800' :
                                        i.improvement_status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                                            i.improvement_status === 'Decline' ? 'bg-red-100 text-red-800' :
                                                'bg-gray-100 text-gray-600'
                                    }`}>
                                    {i.improvement_status || '—'}
                                </span>
                            </div>
                            <div className="mt-3 space-y-2">
                                <div className="flex justify-between text-sm text-gray-600">
                                    <span>{ui.sessions}: {i.sessions_completed ?? 0} / {i.total_sessions_planned ?? '—'}</span>
                                    <span>{i.start_date} → {i.end_date || ui.ongoing}</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div className="h-2 rounded-full bg-purple-500 transition-all"
                                        style={{ width: `${Math.min(i.compliance_percentage || 0, 100)}%` }} />
                                </div>
                                <p className="text-xs text-gray-400 text-right">{i.compliance_percentage?.toFixed(0) ?? 0}% {ui.compliance}</p>
                            </div>
                            {i.provider_name && (
                                <p className="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-100">
                                    {ui.provider}: {i.provider_name} {i.provider_contact ? `· ${i.provider_contact}` : ''}
                                </p>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Disclaimer */}
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 text-sm text-purple-700">
                {ui.warning}
            </div>
        </div>
    );
};

export default ParentDashboard;
