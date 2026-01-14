

// Text-to-Speech Engine with Detailed Reasoning in Telugu and English
class WasteClassifierAudio {
    constructor() {
        this.synth = window.speechSynthesis;
        this.currentLanguage = 'en-US';
        this.isSpeaking = false;
        this.init();
    }

    init() {
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => {
                this.voices = this.synth.getVoices();
            };
        }
    }

    setLanguage(lang) {
        this.currentLanguage = lang;
        localStorage.setItem('wasteClassifierLanguage', lang);
    }

    getLanguage() {
        return localStorage.getItem('wasteClassifierLanguage') || 'en-US';
    }

    speak(text, lang = null) {
        if (!this.synth) {
            console.warn('Speech synthesis not supported');
            return;
        }

        this.synth.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang || this.getLanguage();
        utterance.rate = 0.85;
        utterance.pitch = 1;
        utterance.volume = 1;

        const voices = this.synth.getVoices();
        const voice = voices.find(v => v.lang.startsWith(utterance.lang.split('-')[0]));
        if (voice) {
            utterance.voice = voice;
        }

        utterance.onstart = () => { this.isSpeaking = true; };
        utterance.onend = () => { this.isSpeaking = false; };
        utterance.onerror = (event) => {
            console.error('Speech error:', event);
            this.isSpeaking = false;
        };

        this.synth.speak(utterance);
    }

    stop() {
        if (this.synth) {
            this.synth.cancel();
            this.isSpeaking = false;
        }
    }

    announceResultTelugu(className, confidence) {
        let message = '';
        
        if (className === 'Organic') {
            message = `ఇది సేంద్రియ వ్యర్థం. నమ్మకం స్థాయి ${confidence} శాతం. 
            ఇది సేంద్రియ వ్యర్థం ఎందుకు అనే కారణాలు ఇవి. 
            మొదటిది, ఇది మొక్కలు లేదా జంతువుల వంటి జీవ పదార్థాల నుండి వస్తుంది. 
            రెండవది, ఇందులో సూక్ష్మజీవులు సహజంగా విచ్ఛిన్నం చేయగల జీవ వికలనీయ పదార్థాలు ఉన్నాయి. 
            మూడవది, ఇందులో కార్బన్, నత్రజని మరియు ఇతర పోషకాలతో కూడిన సేంద్రియ సమ్మేళనాలు ఉన్నాయి. 
            నాల్గవది, బ్యాక్టీరియా మరియు శిలీంధ్రాలు సహజ జీవ ప్రక్రియల ద్వారా దీనిని కుళ్ళిపోయేలా చేస్తాయి. 
            ఐదవది, ఇది మట్టిని సమృద్ధి చేసే పోషకాలతో కూడిన కంపోస్ట్ గా మారుతుంది. 
            ఉదాహరణలు ఆహార స్క్రాప్స్, పండ్ల తొక్కలు, కూరగాయల వ్యర్థం, కాఫీ గ్రౌండ్స్. 
            దయచేసి దీన్ని ఆకుపచ్చ లేదా గోధుమ రంగు కంపోస్టింగ్ డబ్బాలో వేయండి. 
            సేంద్రియ వ్యర్థం విలువైన కంపోస్ట్ ను సృష్టిస్తుంది, ల్యాండ్ ఫిల్స్ నుండి మీథేన్ ఉద్గారాలను తగ్గిస్తుంది, మరియు మట్టికి పోషకాలను తిరిగి ఇస్తుంది. ఇది పర్యావరణానికి చాలా మంచిది.`;
        } else if (className === 'Recyclable') {
            message = `ఇది రీసైకిల్ చేయదగిన వ్యర్థం. నమ్మకం స్థాయి ${confidence} శాతం. 
            ఇది రీసైకిల్ చేయదగినది అనే కారణాలు ఇవి. 
            మొదటిది, ఈ పదార్థాన్ని భౌతిక లేదా రసాయన పద్ధతుల ద్వారా తిరిగి ప్రాసెస్ చేయవచ్చు. 
            రెండవది, ఇది జీవ వికలనం కాదు కానీ కరిగించి, పునర్నిర్మాణం చేసి, లేదా కొత్త ఉత్పత్తులుగా మార్చవచ్చు. 
            మూడవది, ప్లాస్టిక్, గాజు, లోహం, కాగితం వంటి పదార్థాలు రీసైకిలింగ్ తర్వాత వాటి లక్షణాలను నిలుపుకుంటాయి. 
            నాల్గవది, ఈ వ్యర్థాన్ని రీసైకిల్ చేయడం ముడి పదార్థాలను సంరక్షిస్తుంది మరియు కొత్త వనరుల అవసరాన్ని తగ్గిస్తుంది. 
            ఐదవది, రీసైకిలింగ్ ప్రక్రియ మొదటి నుండి కొత్త ఉత్పత్తులను సృష్టించడం కంటే తక్కువ శక్తిని ఉపయోగిస్తుంది. 
            ఉదాహరణలు ప్లాస్టిక్ కంటైనర్లు, గాజు సీసాలు, అల్యూమినియం డబ్బాలు, కాగితం ప్యాకేజింగ్. 
            దయచేసి వస్తువును శుభ్రం చేసి నీలం రంగు రీసైకిలింగ్ డబ్బాలో వేయండి. 
            రీసైకిలింగ్ సహజ వనరులను సంరక్షిస్తుంది, శక్తి వినియోగాన్ని తగ్గిస్తుంది, కాలుష్యాన్ని తగ్గిస్తుంది, మరియు భవిష్యత్ తరాలకు పర్యావరణాన్ని రక్షించడంలో సహాయపడుతుంది.`;
        }
        
        this.speak(message, 'te-IN');
    }

    announceResultEnglish(className, confidence) {
        let message = '';
        
        if (className === 'Organic') {
            message = `This is organic waste with ${confidence} percent confidence. 
            This is classified as organic for the following reasons. 
            First, it originates from living organisms like plants or animals. 
            Second, it contains biodegradable materials that microorganisms can break down naturally. 
            Third, it has organic compounds with carbon, nitrogen, and other nutrients. 
            Fourth, bacteria and fungi can decompose it through natural biological processes. 
            Fifth, it can transform into nutrient-rich compost that enriches soil. 
            Examples include food scraps, fruit peels, vegetable waste, and coffee grounds. 
            Please place it in the green or brown composting bin. 
            Organic waste creates valuable compost, reduces methane emissions from landfills, and returns nutrients to the soil, making it highly beneficial for the environment.`;
        } else if (className === 'Recyclable') {
            message = `This is recyclable waste with ${confidence} percent confidence. 
            This is classified as recyclable for the following reasons. 
            First, the material can be reprocessed through physical or chemical methods. 
            Second, it does not biodegrade but can be melted, reformed, or repulped into new products. 
            Third, materials like plastic, glass, metal, and paper retain their properties after recycling. 
            Fourth, recycling this waste conserves raw materials and reduces the need for virgin resources. 
            Fifth, the recycling process uses less energy than creating new products from scratch. 
            Examples include plastic containers, glass bottles, aluminum cans, and paper packaging. 
            Please clean the item and place it in the blue recycling bin. 
            Recycling conserves natural resources, reduces energy consumption, decreases pollution, and helps protect the environment for future generations.`;
        }
        
        this.speak(message, 'en-US');
    }
}

const wasteAudio = new WasteClassifierAudio();
