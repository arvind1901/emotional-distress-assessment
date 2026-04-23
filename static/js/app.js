// ===========================
// GLOBAL STATE
// ===========================

let appState = {
    currentSection: 0,
    role: null,
    demographics: {},
    answers: {},
    questionIds: [],
    config: null
};

const sections = [
    'section-welcome',
    'section-basic',
    'section-demographics',
    'section-questionnaire',
    'section-results'
];

// ===========================
// INITIALIZATION
// ===========================


const FALLBACK_CONFIG = {
    states: [
        "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
        "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
        "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
        "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
        "Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh",
        "Dadra and Nagar Haveli and Daman and Diu","Delhi","Jammu and Kashmir",
        "Ladakh","Lakshadweep","Puducherry"
    ],
    cancerTypes: [
        "Breast Cancer","Lung Cancer","Colorectal Cancer","Prostate Cancer","Stomach Cancer",
        "Liver Cancer","Cervical Cancer","Esophageal Cancer","Thyroid Cancer","Bladder Cancer",
        "Non-Hodgkin Lymphoma","Pancreatic Cancer","Leukemia","Kidney Cancer","Oral Cancer",
        "Brain Tumor","Ovarian Cancer","Skin Cancer (Melanoma)","Blood Cancer","Other"
    ],
    treatmentTypes: [
        "Surgery","Chemotherapy","Radiation Therapy","Immunotherapy","Targeted Therapy",
        "Hormone Therapy","Stem Cell Transplant","Palliative Care","Medication","Other"
    ],
    caregiverQuestions: {
        psychological: [
            { id: "exp_anxiety_depression_emotional_exhaustion", text: "I feel anxiety, depression, or emotional exhaustion." },
            { id: "worry_health_deterioration_possible_death", text: "I worry about health deterioration or possible death." },
            { id: "feel_guilty", text: "I feel guilty." },
            { id: "unclear_expectations", text: "Caregiving expectations are unclear." }
        ],
        social: [
            { id: "social_activities_reduced", text: "My social activities are reduced." },
            { id: "strained_relationships", text: "My relationships are strained." },
            { id: "give_up_hobbies", text: "I have given up hobbies or personal interests." },
            { id: "little_no_time_for_yourself", text: "I have little or no time for myself." },
            { id: "burden", text: "I feel caregiving is a burden." },
            { id: "overwhelmed", text: "I feel overwhelmed." },
            { id: "affected_performance", text: "My performance (work/role) is affected." }
        ],
        sleep_physical: [
            { id: "sleep_disturbed", text: "My sleep is disturbed." },
            { id: "rest_sleep", text: "I get restful sleep." },
            { id: "physically_exhausted", text: "I feel physically exhausted." }
        ],
        financial: [
            { id: "lost_income_leave_work", text: "I have lost income or had to leave work." },
            { id: "medical_expenses_increased", text: "Medical expenses have increased." },
            { id: "risk_jobloss", text: "I worry about losing my job." },
            { id: "missed_ownmedical", text: "I missed my own medical appointments." }
        ],
        care_management: [
            { id: "difficult_to_manage", text: "Managing the patient's care is difficult." }
        ],
        protective: [
            { id: "closer_to_patient", text: "Caregiving makes me feel closer to the patient." },
            { id: "sense_of_purpose", text: "Caregiving gives me a sense of purpose." }
        ]
    },
    patientQuestions: {
        emotional: [
            { id: "feel_tense", text: "I feel tense." },
            { id: "worry", text: "I worry." },
            { id: "feel_depressed", text: "I feel depressed." },
            { id: "feel_uncertain", text: "I feel uncertain about my health/future." }
        ],
        physical: [
            { id: "pain", text: "I experience pain." },
            { id: "felt_nauseated", text: "I feel nauseated." },
            { id: "felt_weak", text: "I feel weak." },
            { id: "lacked_appetite", text: "I lack appetite." }
        ],
        sleep: [
            { id: "tired", text: "I feel tired." },
            { id: "need_to_rest", text: "I need to rest." },
            { id: "trouble_sleeping", text: "I have trouble sleeping." }
        ]
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const config = await loadConfig();
        appState.config = normalizeConfig(config);

        // Populate dropdowns
        populateStates();
        populateCancerTypes();
        populateTreatmentTypes();

        // Setup event listeners
        setupEventListeners();

        console.log('App initialized successfully');
    } catch (error) {
        console.error('Initialization error:', error);
        alert('Failed to load application. Please refresh the page.');
    }
});

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        if (!response.ok) {
            throw new Error('Config request failed');
        }
        return await response.json();
    } catch (error) {
        console.warn('Using fallback configuration due to error:', error);
        return FALLBACK_CONFIG;
    }
}

function normalizeConfig(config) {
    const safeConfig = config || {};
    return {
        states: Array.isArray(safeConfig.states) && safeConfig.states.length ? safeConfig.states : FALLBACK_CONFIG.states,
        cancerTypes: Array.isArray(safeConfig.cancerTypes) && safeConfig.cancerTypes.length ? safeConfig.cancerTypes : FALLBACK_CONFIG.cancerTypes,
        treatmentTypes: Array.isArray(safeConfig.treatmentTypes) && safeConfig.treatmentTypes.length ? safeConfig.treatmentTypes : FALLBACK_CONFIG.treatmentTypes,
        caregiverQuestions: safeConfig.caregiverQuestions || FALLBACK_CONFIG.caregiverQuestions,
        patientQuestions: safeConfig.patientQuestions || FALLBACK_CONFIG.patientQuestions
    };
}


// ===========================
// POPULATE FORM ELEMENTS
// ===========================

function populateStates() {
    const stateSelect = document.getElementById('state');
    appState.config.states.forEach(state => {
        const option = document.createElement('option');
        option.value = state;
        option.textContent = state;
        stateSelect.appendChild(option);
    });
}

function populateCancerTypes() {
    const cancerSelect = document.getElementById('cancer-type');
    appState.config.cancerTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        cancerSelect.appendChild(option);
    });
}

function populateTreatmentTypes() {
    const treatmentContainer = document.getElementById('treatment-types');
    appState.config.treatmentTypes.forEach(treatment => {
        const label = document.createElement('label');
        label.className = 'checkbox-label';
        label.innerHTML = `
            <input type="checkbox" name="treatment" value="${treatment}">
            <span>${treatment}</span>
        `;
        treatmentContainer.appendChild(label);
    });
}

// ===========================
// EVENT LISTENERS
// ===========================

function setupEventListeners() {
    // Patient alive status
    const patientAliveRadios = document.getElementsByName('patient-alive');
    patientAliveRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const deathDateField = document.getElementById('death-date-field');
            if (e.target.value === 'no') {
                deathDateField.style.display = 'block';
            } else {
                deathDateField.style.display = 'none';
            }
        });
    });
}

// ===========================
// NAVIGATION
// ===========================

function showSection(sectionIndex) {
    // Hide all sections
    sections.forEach((sectionId, index) => {
        const section = document.getElementById(sectionId);
        if (index === sectionIndex) {
            section.classList.add('active');
        } else {
            section.classList.remove('active');
        }
    });
    
    // Update progress
    updateProgress(sectionIndex);
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    appState.currentSection = sectionIndex;
}

function updateProgress(sectionIndex) {
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (sectionIndex === 0) {
        progressContainer.style.display = 'none';
    } else {
        progressContainer.style.display = 'block';
        const progress = ((sectionIndex) / (sections.length - 1)) * 100;
        progressFill.style.width = progress + '%';
        progressText.textContent = `Step ${sectionIndex} of ${sections.length - 1}`;
    }
}

function nextSection() {
    if (appState.currentSection < sections.length - 1) {
        showSection(appState.currentSection + 1);
    }
}

function previousSection() {
    if (appState.currentSection > 0) {
        showSection(appState.currentSection - 1);
    }
}

// ===========================
// SECTION 1: AGE VERIFICATION
// ===========================

function handleAgeVerification() {
    const selectedAge = document.querySelector('input[name="age-verify"]:checked');
    const underageMessage = document.getElementById('underage-message');
    
    if (!selectedAge) {
        alert('Please select an option');
        return;
    }
    
    if (selectedAge.value === 'no') {
        underageMessage.style.display = 'block';
        return;
    }
    
    underageMessage.style.display = 'none';
    nextSection();
}

// ===========================
// SECTION 2: ROLE SELECTION
// ===========================

function handleRoleSelection() {
    const state = document.getElementById('state').value;
    const role = document.querySelector('input[name="role"]:checked');
    
    if (!state) {
        alert('Please select your state of residence');
        return;
    }
    
    if (!role) {
        alert('Please select your role');
        return;
    }
    
    appState.role = role.value;
    appState.demographics.state = state;
    
    // Show/hide caregiver-specific fields
    const caregiverFields = document.getElementById('caregiver-fields');
    if (appState.role === 'caregiver') {
        caregiverFields.style.display = 'block';
        document.getElementById('diagnosis-label').textContent = "Patient's Diagnosis Date (MM/YYYY) *";
        document.getElementById('cancer-type-label').textContent = "Patient's Cancer Type *";
    } else {
        caregiverFields.style.display = 'none';
        document.getElementById('diagnosis-label').textContent = "Your Diagnosis Date (MM/YYYY) *";
        document.getElementById('cancer-type-label').textContent = "Your Cancer Type *";
    }
    
    nextSection();
}

// ===========================
// SECTION 3: DEMOGRAPHICS
// ===========================

function validateDemographics() {
    const ageGroup = document.getElementById('age-group').value;
    const gender = document.querySelector('input[name="gender"]:checked');
    const diagnosisDate = document.getElementById('diagnosis-date').value;
    const cancerType = document.getElementById('cancer-type').value;
    const ngoHelp = document.getElementById('ngo-help').value;
    
    // Check required fields
    if (!ageGroup || !gender || !diagnosisDate || !cancerType || !ngoHelp) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Get selected treatments
    const treatmentCheckboxes = document.querySelectorAll('input[name="treatment"]:checked');
    if (treatmentCheckboxes.length === 0) {
        alert('Please select at least one treatment type');
        return;
    }
    const treatments = Array.from(treatmentCheckboxes).map(cb => cb.value);
    
    // Store demographics
    appState.demographics.age_group = parseInt(ageGroup);
    appState.demographics.gender = parseInt(gender.value);
    appState.demographics.diagnosis_date = diagnosisDate;
    appState.demographics.cancer_type = cancerType;
    appState.demographics.treatments = treatments;
    appState.demographics.ngo_help = ngoHelp;
    
    // Caregiver-specific fields
    if (appState.role === 'caregiver') {
        const relation = document.getElementById('relation').value;
        const patientAlive = document.querySelector('input[name="patient-alive"]:checked');
        
        if (!relation || !patientAlive) {
            alert('Please fill in all caregiver-specific fields');
            return;
        }
        
        appState.demographics.relation = relation;
        appState.demographics.patient_alive = patientAlive.value;
        
        if (patientAlive.value === 'no') {
            const deathDate = document.getElementById('death-date').value;
            if (!deathDate) {
                alert('Please provide the date of death');
                return;
            }
            appState.demographics.death_date = deathDate;
        }
    }
    
    // Generate questionnaire
    generateQuestionnaire();
    nextSection();
}

// ===========================
// SECTION 4: QUESTIONNAIRE
// ===========================

function generateQuestionnaire() {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';
    
    let questions;
    if (appState.role === 'caregiver') {
        questions = appState.config.caregiverQuestions;
        document.getElementById('questionnaire-title').textContent = 'Caregiver Assessment Questions';
    } else {
        questions = appState.config.patientQuestions;
        document.getElementById('questionnaire-title').textContent = 'Patient Assessment Questions';
    }
    
    // Reset answers
    appState.answers = {};
    appState.questionIds = [];
    
    // Generate question blocks for each domain
    Object.keys(questions).forEach(domain => {
        const domainQuestions = questions[domain];
        
        const domainBlock = document.createElement('div');
        domainBlock.className = 'question-block';
        
        // Domain title
        const domainTitle = document.createElement('div');
        domainTitle.className = 'question-domain';
        domainTitle.innerHTML = `<span>📋</span> ${formatDomainName(domain)}`;
        domainBlock.appendChild(domainTitle);
        
        // Questions
        domainQuestions.forEach((question, qIndex) => {
            const questionItem = document.createElement('div');
            questionItem.className = 'question-item';
            
            const questionTextDiv = document.createElement('div');
            questionTextDiv.className = 'question-text';
            const questionId = typeof question === 'string' ? `${domain}_${qIndex}` : question.id;
            const questionText = typeof question === 'string' ? question : question.text;
            appState.questionIds.push(questionId);
            questionTextDiv.textContent = `${qIndex + 1}. ${questionText}`;
            questionItem.appendChild(questionTextDiv);
            
            // Scale options
            const scaleOptions = document.createElement('div');
            scaleOptions.className = 'scale-options';
            
            for (let i = 1; i <= 5; i++) {
                const scaleOption = document.createElement('div');
                scaleOption.className = 'scale-option';
                
                const radioId = `${questionId}_${i}`;
                const radio = document.createElement('input');
                radio.type = 'radio';
                radio.name = questionId;
                radio.value = i;
                radio.id = radioId;
                radio.addEventListener('change', () => {
                    appState.answers[questionId] = i;
                });
                
                const label = document.createElement('label');
                label.htmlFor = radioId;
                label.innerHTML = `
                    <span class="scale-number">${i}</span>
                    <span class="scale-label-small">${getScaleLabel(i)}</span>
                `;
                
                scaleOption.appendChild(radio);
                scaleOption.appendChild(label);
                scaleOptions.appendChild(scaleOption);
            }
            
            questionItem.appendChild(scaleOptions);
            domainBlock.appendChild(questionItem);
        });
        
        container.appendChild(domainBlock);
    });
}

function formatDomainName(domain) {
    const names = {
        'psychological': 'Psychological',
        'social': 'Social & Emotional Burden',
        'sleep_physical': 'Sleep & Physical',
        'financial': 'Financial & Work Impact',
        'care_management': 'Care Management',
        'protective': 'Protective Factors',
        'emotional': 'Emotional',
        'physical': 'Physical Symptoms',
        'sleep': 'Sleep'
    };
    return names[domain] || domain.replace('_', ' ').toUpperCase();
}

function getScaleLabel(value) {
    const labels = {
        1: 'Not at all',
        2: 'Slightly',
        3: 'Moderately',
        4: 'Quite a bit',
        5: 'Extremely'
    };
    return labels[value] || '';
}

// ===========================
// SECTION 5: SUBMISSION
// ===========================

async function submitAssessment() {
    // Validate all questions answered
    const allAnswered = appState.questionIds.every(id => appState.answers[id] !== undefined && appState.answers[id] !== null);

    if (!allAnswered) {
        alert('Please answer all questions before submitting');
        return;
    }

    // Show loading
    document.getElementById('loading-overlay').style.display = 'flex';

    try {
        // Prepare data
        const payload = {
            role: appState.role,
            demographics: appState.demographics,
            answers: appState.answers
        };

        // Send to backend
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json().catch(() => ({}));

        if (!response.ok || !result.success) {
            const message = result.error || 'Prediction failed';
            throw new Error(message);
        }

        // Hide loading
        document.getElementById('loading-overlay').style.display = 'none';

        // Show results
        displayResults(result);
        nextSection();

    } catch (error) {
        console.error('Submission error:', error);
        document.getElementById('loading-overlay').style.display = 'none';
        alert(`An error occurred while processing your assessment: ${error.message}`);
    }
}


function displayResults(result) {
    const container = document.getElementById('results-content');
    
    const predictionClass = result.prediction.toLowerCase();
    const icon = {
        'low': '😊',
        'moderate': '😐',
        'high': '😟'
    }[predictionClass] || '📊';
    
    let html = `
        <div class="result-header">
            <div class="result-icon">${icon}</div>
            <h2 class="result-title">Assessment Complete</h2>
            <div class="result-prediction ${predictionClass}">
                ${result.prediction} Emotional Distress
            </div>
            ${result.confidence ? `
                <p><span class="confidence-badge">Confidence: ${(result.confidence * 100).toFixed(1)}%</span></p>
            ` : ''}
        </div>
        
        <div class="result-interpretation">
            <p>${result.interpretation}</p>
        </div>
        
        <div class="scores-section">
            <h3>📊 Your Domain Scores</h3>
            <p class="info-text">Scores range from 1.0 (lowest) to 5.0 (highest)</p>
    `;
    
    Object.keys(result.scores).forEach(scoreName => {
        html += `
            <div class="score-item">
                <span class="score-label">${scoreName}</span>
                <span class="score-value">${result.scores[scoreName]} / 5.0</span>
            </div>
        `;
    });
    
    html += `
        </div>
        
        <div class="info-text" style="margin-top: 2rem;">
            <strong>📞 Need Support?</strong><br>
            If you're experiencing significant distress, please consider reaching out to:
            <ul style="margin-top: 0.5rem; margin-left: 1.5rem;">
                <li>Your healthcare provider</li>
                <li>A mental health professional</li>
                <li>Cancer support organizations</li>
                <li>Support groups in your area</li>
            </ul>
        </div>
        
        <div class="info-text" style="margin-top: 1rem;">
            <strong>ℹ️ About This Assessment</strong><br>
            This tool provides an indication of emotional distress levels based on validated questionnaires. 
            It is not a clinical diagnosis and should not replace professional medical advice.
        </div>
    `;
    
    container.innerHTML = html;
}

// ===========================
// RESET
// ===========================

function resetAssessment() {
    // Reset state
    appState = {
        currentSection: 0,
        role: null,
        demographics: {},
        answers: {},
        config: appState.config
    };
    
    // Reset form inputs
    document.querySelectorAll('input[type="radio"]').forEach(input => input.checked = false);
    document.querySelectorAll('input[type="checkbox"]').forEach(input => input.checked = false);
    document.querySelectorAll('select').forEach(select => select.selectedIndex = 0);
    document.querySelectorAll('input[type="month"]').forEach(input => input.value = '');
    
    // Show first section
    showSection(0);
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}
