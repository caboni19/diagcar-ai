const DIAGCAR_TRANSLATIONS = {
  en: {
    nav_home:'Home', nav_dashboard:'Dashboard', nav_diagnostic:'Diagnostic Wizard', nav_logout:'Logout', nav_login:'Login', nav_register:'Create account', start:'Start',
    hero_welcome:'WELCOME TO DIAG CAR', hero_title:'Smart Vehicle <span>Diagnostics</span> Powered by AI', hero_lead:'Understand your car before the mechanic does. DZ Nova analyzes symptoms, explains probable faults and guides you with practical recommendations.', launch_wizard:'Start Diagnosis', open_dashboard:'My Vehicle', create_account:'Create account', footer_note:'AI vehicle diagnostics built for clear, multilingual and practical decisions.',
    feature1_title:'AI-powered analysis', feature1_text:'The engine interprets symptoms and ranks probable faults.', feature2_title:'Multilingual support', feature2_text:'Arabic, French, English and Algerian Darija are supported.', feature3_title:'Clear reports', feature3_text:'Every result includes probability, severity and recommended action.', workflow_title:'A cleaner way to understand vehicle problems', workflow_1_title:'Save your vehicle', workflow_1_text:'The user enters the car profile once during registration.', workflow_2_title:'Describe the symptom', workflow_2_text:'The chat accepts normal language, French, Arabic and Darija.', workflow_3_title:'Receive a smart report', workflow_3_text:'The system returns a professional diagnostic card with explanation.',
    command_center:'Command Center', welcome:'Welcome', new_diag:'+ New diagnostic', new_chat:'+ New AI chat', dashboard_lead:'Your saved car profile is already loaded. Start a diagnostic chat when a new symptom appears.', saved_vehicle:'Saved vehicle profile', start_ai_chat:'Start AI diagnostic chat', brand:'Brand', model:'Model', year:'Year', fuel:'Fuel type', transmission:'Transmission', mileage:'Mileage', total_diagnostics:'Total diagnostics', your_vehicle:'Your vehicle', nlp_obd:'NLP + OBD scoring', recent_diagnostics:'Recent diagnostics', loading:'Loading...',
    secure_access:'Secure Access', login_title:'Login', login_text:'Access your DZ Nova dashboard, vehicle history and AI reports.', email:'Email', password:'Password', login_btn:'Login', no_account:'No account?', register_link:'Register', create_driver:'Create Driver Profile', register_text:'Your account is saved in MySQL and your vehicle profile will be reused automatically in the AI diagnostic chat.', first_name:'First name *', last_name:'Last name', email_required:'Email *', phone:'Phone', password_required:'Password *', register_btn:'Register', already_account:'Already have an account?', driver_info:'Driver information', vehicle_info:'Vehicle information', brand_logo_hint:'The logo updates according to the selected manufacturer', mileage_ph:'Mileage',
    chat_badge:'AI Diagnostic Chat', chat_title:'Describe the symptom. Your car profile is already loaded.', chat_lead:'The system uses the vehicle information saved during registration, so the user only needs to explain what is happening now.', active_vehicle:'Active vehicle', symptom_chat:'Diagnostic conversation', vehicle_loaded:'Vehicle profile loaded', chat_intro:'Hello. Tell me the symptoms you noticed: sound, smoke, warning light, overheating, braking issue, or anything unusual.', symptoms_ph:'Example: engine light is on, the car overheats and black smoke appears...', voice:'🎙 Voice', send_to_ai:'Send to AI', q1:'Engine light + consumption', q2:'Overheating + oil', q3:'Startup noise', q4:'Braking'
  },
  fr: {
    nav_home:'Accueil', nav_dashboard:'Tableau de bord', nav_diagnostic:'Assistant Diagnostic', nav_logout:'Déconnexion', nav_login:'Connexion', nav_register:'Créer un compte', start:'Commencer',
    hero_welcome:'BIENVENUE SUR DIAG CAR', hero_title:'Diagnostic <span>intelligent</span> des véhicules par IA', hero_lead:'Comprenez votre voiture avant le mécanicien. DZ Nova analyse les symptômes, explique les pannes probables et propose des recommandations pratiques.', launch_wizard:'Démarrer le diagnostic', open_dashboard:'Mon véhicule', create_account:'Créer un compte', footer_note:'Diagnostic automobile IA conçu pour des décisions claires, multilingues et pratiques.',
    feature1_title:'Analyse par IA', feature1_text:'Le moteur interprète les symptômes et classe les pannes probables.', feature2_title:'Support multilingue', feature2_text:'Arabe, français, anglais et darija algérienne sont pris en charge.', feature3_title:'Rapports clairs', feature3_text:'Chaque résultat inclut probabilité, gravité et action recommandée.', workflow_title:'Une manière plus claire de comprendre les problèmes du véhicule', workflow_1_title:'Enregistrer le véhicule', workflow_1_text:'L’utilisateur saisit le profil du véhicule une seule fois lors de l’inscription.', workflow_2_title:'Décrire le symptôme', workflow_2_text:'Le chat accepte le langage naturel, le français, l’arabe et la darija.', workflow_3_title:'Recevoir un rapport intelligent', workflow_3_text:'Le système affiche une carte de diagnostic professionnelle avec explication.',
    command_center:'Centre de contrôle', welcome:'Bienvenue', new_diag:'+ Nouveau diagnostic', new_chat:'+ Nouveau chat IA', dashboard_lead:'Le profil de votre voiture est déjà chargé. Lancez une conversation de diagnostic quand un nouveau symptôme apparaît.', saved_vehicle:'Profil véhicule enregistré', start_ai_chat:'Démarrer le chat diagnostic IA', brand:'Marque', model:'Modèle', year:'Année', fuel:'Type de carburant', transmission:'Transmission', mileage:'Kilométrage', total_diagnostics:'Total des diagnostics', your_vehicle:'Votre véhicule', nlp_obd:'NLP + score OBD', recent_diagnostics:'Diagnostics récents', loading:'Chargement...',
    secure_access:'Accès sécurisé', login_title:'Connexion', login_text:'Accédez à votre tableau de bord DZ Nova, historique véhicule et rapports IA.', email:'Email', password:'Mot de passe', login_btn:'Connexion', no_account:'Pas de compte ?', register_link:'Inscription', create_driver:'Créer un profil conducteur', register_text:'Votre compte est enregistré dans MySQL et votre profil véhicule sera réutilisé automatiquement dans le chat IA.', first_name:'Prénom *', last_name:'Nom', email_required:'Email *', phone:'Téléphone', password_required:'Mot de passe *', register_btn:'S’inscrire', already_account:'Vous avez déjà un compte ?', driver_info:'Informations conducteur', vehicle_info:'Informations véhicule', brand_logo_hint:'Le logo change selon la marque sélectionnée', mileage_ph:'Kilométrage',
    chat_badge:'Chat de diagnostic IA', chat_title:'Décrivez le symptôme. Le profil de votre voiture est déjà chargé.', chat_lead:'Le système utilise les informations véhicule enregistrées lors de l’inscription. L’utilisateur décrit seulement le problème actuel.', active_vehicle:'Véhicule actif', symptom_chat:'Conversation de diagnostic', vehicle_loaded:'Profil véhicule chargé', chat_intro:'Bonjour. Décrivez les symptômes remarqués : bruit, fumée, voyant, surchauffe, freinage ou comportement inhabituel.', symptoms_ph:'Exemple : voyant moteur allumé, voiture qui chauffe et fumée noire...', voice:'🎙 Voix', send_to_ai:'Envoyer à l’IA', q1:'Voyant moteur + consommation', q2:'Surchauffe + huile', q3:'Bruit au démarrage', q4:'Freinage'
  },
  ar: {
    nav_home:'الرئيسية', nav_dashboard:'لوحة التحكم', nav_diagnostic:'معالج التشخيص', nav_logout:'تسجيل الخروج', nav_login:'تسجيل الدخول', nav_register:'إنشاء حساب', start:'ابدأ',
    hero_welcome:'مرحباً بك في DIAG CAR', hero_title:'تشخيص <span>ذكي</span> لأعطال السيارات بالذكاء الاصطناعي', hero_lead:'افهم سيارتك قبل الذهاب إلى الميكانيكي. يحلل DZ Nova الأعراض، يشرح الأعطال المحتملة، ويقترح عليك خطوات عملية واضحة.', launch_wizard:'ابدأ التشخيص', open_dashboard:'سيارتي', create_account:'إنشاء حساب', footer_note:'تشخيص سيارات بالذكاء الاصطناعي، متعدد اللغات، واضح وعملي.',
    feature1_title:'تحليل مدعوم بالذكاء الاصطناعي', feature1_text:'يقوم المحرك بفهم الأعراض وترتيب الأعطال المحتملة.', feature2_title:'دعم متعدد اللغات', feature2_text:'يدعم العربية، الفرنسية، الإنجليزية والدارجة الجزائرية.', feature3_title:'تقارير واضحة', feature3_text:'كل نتيجة تحتوي على الاحتمال، الخطورة، والإجراء المقترح.', workflow_title:'طريقة أوضح لفهم مشاكل السيارة', workflow_1_title:'حفظ معلومات السيارة', workflow_1_text:'يدخل المستخدم معلومات سيارته مرة واحدة أثناء التسجيل.', workflow_2_title:'وصف الأعراض', workflow_2_text:'المحادثة تقبل اللغة العادية، العربية، الفرنسية والدارجة.', workflow_3_title:'استلام تقرير ذكي', workflow_3_text:'يعرض النظام بطاقة تشخيص احترافية مع شرح واضح.',
    command_center:'مركز التحكم', welcome:'مرحباً', new_diag:'+ تشخيص جديد', new_chat:'+ محادثة ذكاء اصطناعي جديدة', dashboard_lead:'معلومات سيارتك محفوظة ومحملة تلقائياً. افتح محادثة تشخيص عندما تظهر أعراض جديدة.', saved_vehicle:'معلومات السيارة المحفوظة', start_ai_chat:'ابدأ محادثة التشخيص الذكي', brand:'العلامة', model:'الطراز', year:'السنة', fuel:'نوع الوقود', transmission:'ناقل الحركة', mileage:'عدد الكيلومترات', total_diagnostics:'عدد التشخيصات', your_vehicle:'سيارتك', nlp_obd:'تحليل لغوي + أكواد OBD', recent_diagnostics:'آخر التشخيصات', loading:'جاري التحميل...',
    secure_access:'دخول آمن', login_title:'تسجيل الدخول', login_text:'ادخل إلى لوحة DZ Nova وسجل السيارة وتقارير الذكاء الاصطناعي.', email:'البريد الإلكتروني', password:'كلمة المرور', login_btn:'تسجيل الدخول', no_account:'ليس لديك حساب؟', register_link:'سجل الآن', create_driver:'إنشاء ملف السائق', register_text:'يتم حفظ حسابك في MySQL وإعادة استخدام معلومات السيارة تلقائياً داخل محادثة التشخيص.', first_name:'الاسم *', last_name:'اللقب', email_required:'البريد الإلكتروني *', phone:'الهاتف', password_required:'كلمة المرور *', register_btn:'تسجيل', already_account:'لديك حساب بالفعل؟', driver_info:'معلومات السائق', vehicle_info:'معلومات السيارة', brand_logo_hint:'يتغير الشعار حسب الشركة المصنعة المختارة', mileage_ph:'عدد الكيلومترات',
    chat_badge:'محادثة التشخيص الذكي', chat_title:'اكتب الأعراض فقط. معلومات سيارتك محملة مسبقاً.', chat_lead:'يعتمد النظام على معلومات السيارة المحفوظة أثناء التسجيل، لذلك المستخدم يصف المشكلة الحالية فقط.', active_vehicle:'السيارة النشطة', symptom_chat:'محادثة التشخيص', vehicle_loaded:'تم تحميل معلومات السيارة', chat_intro:'مرحباً. اشرح الأعراض التي لاحظتها: صوت، دخان، ضوء تحذير، ارتفاع حرارة، مشكلة فرامل أو أي شيء غير عادي.', symptoms_ph:'مثال: ضو moteur شاعل والسيارة تسخن والدخان أسود...', voice:'🎙 صوت', send_to_ai:'أرسل للذكاء الاصطناعي', q1:'ضوء المحرك + استهلاك زائد', q2:'ارتفاع الحرارة + الزيت', q3:'صوت عند التشغيل', q4:'الفرامل'
  }
};

function getCurrentLang(){ return localStorage.getItem('diagcar_lang') || 'en'; }
function applyLanguage(lang){
  const dict = DIAGCAR_TRANSLATIONS[lang] || DIAGCAR_TRANSLATIONS.en;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  document.body.classList.toggle('rtl', lang === 'ar');
  document.body.classList.toggle('ltr', lang !== 'ar');
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const key = el.getAttribute('data-i18n');
    if(dict[key]) el.innerHTML = dict[key];
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{
    const key = el.getAttribute('data-i18n-placeholder');
    if(dict[key]){
      if(el.tagName === 'SELECT' && el.options.length){ el.options[0].textContent = dict[key]; }
      else el.setAttribute('placeholder', dict[key]);
    }
  });
}

document.addEventListener('DOMContentLoaded', ()=>{
  const sel = document.getElementById('langSwitcher');
  const lang = getCurrentLang();
  if(sel) sel.value = lang;
  applyLanguage(lang);
  if(sel){
    sel.addEventListener('change', ()=>{
      localStorage.setItem('diagcar_lang', sel.value);
      applyLanguage(sel.value);
    });
  }
});
