
const BRAND_LOGOS = {
  'renault':'renault.png',
  'peugeot':'peugeot.png',
  'hyundai':'hyundai.png',
  'kia':'kia.png',
  'toyota':'toyota.png',
  'volkswagen':'volkswagen.png',
  'mercedes':'mercedes.png',
  'mercedes-benz':'mercedes.png',
  'bmw':'bmw.png',
  'ford':'ford.png',
  'audi':'audi.png',
  'dacia':'default.svg',
  'seat':'default.svg',
  'nissan':'default.svg',
  'citroen':'default.svg',
  'fiat':'default.svg',
  'opel':'default.svg'
};
function brandSlug(brand=''){
  return String(brand || '')
    .trim()
    .toLowerCase()
    .replace(/&/g,'and')
    .replace(/[^a-z0-9]+/g,'-')
    .replace(/^-+|-+$/g,'') || 'default';
}
function brandLogoSrc(brand=''){
  const slug = brandSlug(brand);
  const file = BRAND_LOGOS[slug] || `${slug}.png`;
  return `/static/img/brands/${file}`;
}
function setupBrandPreview(){
  const select = document.getElementById('carBrand');
  const img = document.getElementById('brandLogoPreview');
  const label = document.getElementById('brandPreviewName');
  if (!select || !img) return;
  const update = () => {
    const brand = select.value || 'DZ Nova';
    img.src = brandLogoSrc(brand);
    if (label) label.textContent = brand;
  };
  select.addEventListener('change', update);
  update();
}
document.addEventListener('DOMContentLoaded', setupBrandPreview);
const symptoms = document.getElementById('symptoms');
const result = document.getElementById('result');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');

document.querySelectorAll('[data-q]').forEach((button) => {
  button.addEventListener('click', () => {
    symptoms.value = `${symptoms.value ? symptoms.value + '\n' : ''}${button.dataset.q}`;
    symptoms.focus();
  });
});

function vehiclePayload() {
  const saved = window.DIAGCAR_USER_VEHICLE || {};
  return {
    brand: saved.brand || document.getElementById('brand')?.value || '',
    model: saved.model || document.getElementById('model')?.value || '',
    year: saved.year || document.getElementById('year')?.value || '',
    fuel: saved.fuel || document.getElementById('fuel')?.value || '',
    transmission: saved.transmission || document.getElementById('transmission')?.value || '',
    mileage: saved.mileage || document.getElementById('mileage')?.value || ''
  };
}

function appendUserMessage(text) {
  const chatThread = document.getElementById('chatThread');
  if (!chatThread || !text) return;
  const bubble = document.createElement('div');
  bubble.className = 'user-message';
  bubble.textContent = text;
  chatThread.appendChild(bubble);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function appendBotMessage(text) {
  const chatThread = document.getElementById('chatThread');
  if (!chatThread || !text) return;
  const bubble = document.createElement('div');
  bubble.className = 'bot-message';
  bubble.textContent = text;
  chatThread.appendChild(bubble);
  chatThread.scrollTop = chatThread.scrollHeight;
}

function currentLang(text = '') {
  const selected = localStorage.getItem('diagcar_lang');
  if (selected) return selected;
  if (/[\u0600-\u06FF]/.test(text)) return 'ar';
  if (/(voiture|moteur|frein|huile|fumée|problème|bruit)/i.test(text)) return 'fr';
  return 'en';
}

const RESULT_I18N = {
  en: { report:'Diagnostic Report', brand:'Brand', model:'Model', health:'Vehicle health score', most:'Most probable', alt:'Alternative', prob:'Probability', sev:'Severity', cat:'Category', obd:'OBD', exp:'Explanation', rec:'Recommended action', why:'Why this diagnosis?', nodata:'No result found.', empty:'Please describe symptoms first.', loading:'AI engine is analyzing...', loadingText:'Matching multilingual symptoms with the diagnostic knowledge base.', pdf:'Export PDF Report', backend:'Backend error. Check Flask, XAMPP/MySQL and the /api/diagnose route.', workshopTitle:'Need a nearby repair workshop?', workshopText:'Use your current location to open nearby garages and mechanics in Google Maps.', workshopBtn:'Find nearby workshops', workshopHint:'Your browser will ask for location permission.', workshopNoGeo:'Geolocation is not supported by your browser.', workshopDenied:'Location permission is required to find nearby workshops.' },
  fr: { report:'Rapport de diagnostic', brand:'Marque', model:'Modèle', health:'Score de santé', most:'Diagnostic principal', alt:'Alternative', prob:'Probabilité', sev:'Gravité', cat:'Catégorie', obd:'OBD', exp:'Explication', rec:'Action recommandée', why:'Pourquoi ce diagnostic ?', nodata:'Aucun résultat trouvé.', empty:'Veuillez décrire les symptômes d’abord.', loading:'Le moteur IA analyse...', loadingText:'Correspondance des symptômes multilingues avec la base de diagnostic.', pdf:'Exporter le rapport PDF', backend:'Erreur backend. Vérifiez Flask, XAMPP/MySQL et la route /api/diagnose.', workshopTitle:'Besoin d’un garage proche ?', workshopText:'Utilisez votre position actuelle pour ouvrir les garages et mécaniciens proches dans Google Maps.', workshopBtn:'Trouver les garages proches', workshopHint:'Le navigateur demandera l’autorisation de localisation.', workshopNoGeo:'La géolocalisation n’est pas prise en charge par ce navigateur.', workshopDenied:'L’autorisation de localisation est nécessaire pour trouver les garages proches.' },
  ar: { report:'تقرير التشخيص', brand:'العلامة', model:'الطراز', health:'مؤشر صحة السيارة', most:'الاحتمال الأكبر', alt:'بديل', prob:'نسبة الاحتمال', sev:'الخطورة', cat:'الفئة', obd:'رمز العطل', exp:'الشرح', rec:'الإجراء الموصى به', why:'لماذا هذا التشخيص؟', nodata:'لم يتم العثور على نتائج.', empty:'اكتب وصف الأعراض أولاً.', loading:'يقوم الذكاء الاصطناعي بالتحليل...', loadingText:'تتم مطابقة الأعراض متعددة اللغات مع قاعدة التشخيص.', pdf:'تصدير تقرير PDF', backend:'خطأ في الخادم. تحقق من Flask و XAMPP/MySQL ومسار /api/diagnose.', workshopTitle:'تحتاج إلى أقرب ورشة؟', workshopText:'استعمل موقعك الحالي لفتح أقرب ورشات وميكانيكيين عبر خرائط Google.', workshopBtn:'البحث عن أقرب ورشة', workshopHint:'سيطلب المتصفح إذن تحديد الموقع.', workshopNoGeo:'المتصفح لا يدعم تحديد الموقع.', workshopDenied:'يجب السماح بتحديد الموقع للعثور على أقرب الورشات.' }
};

if (sendBtn) {
  sendBtn.addEventListener('click', async () => {
    // ── SUBSCRIPTION GATE (7 free diagnostics limit) ──
    if (window.DiagCarSub && !window.DiagCarSub.checkAllowed()) {
      return; // paywall modal shown by checkAllowed()
    }
    const text = symptoms.value.trim();
    const lang = currentLang(text);
    const t = RESULT_I18N[lang] || RESULT_I18N.en;

    if (!text) {
      result.innerHTML = `<article class="result-card"><p>${t.empty}</p></article>`;
      return;
    }

    appendUserMessage(text);
    sendBtn.disabled = true;
    result.innerHTML = `<article class="result-card"><span class="badge">AI</span><h2>${t.loading}</h2><p class="muted">${t.loadingText}</p></article>`;

    try {
      const response = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, vehicle: vehiclePayload(), lang })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      renderResults(data, lang);
      // ── Record usage after successful diagnosis ──
      if (window.DiagCarSub) window.DiagCarSub.recordUsed();
      appendBotMessage(data.chat_response || ((RESULT_I18N[lang] || RESULT_I18N.en).report + ' ready. Check the detailed result below.'));
      symptoms.value = '';
    } catch (error) {
      console.error(error);
      result.innerHTML = `<article class="result-card"><span class="badge">ERROR</span><h2>${t.backend}</h2></article>`;
    } finally {
      sendBtn.disabled = false;
    }
  });
}

function renderResults(data, lang = currentLang(symptoms.value)) {
  const t = RESULT_I18N[lang] || RESULT_I18N.en;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';

  const results = Array.isArray(data?.results) ? data.results : [];
  if (!results.length) {
    result.innerHTML = `<article class="result-card premium-empty"><p>${t.nodata}</p></article>`;
    return;
  }

  const vehicle = data.vehicle || vehiclePayload();
  const top = results[0];
  const score = healthScore(top);
  const probability = Math.max(0, Math.min(100, Number(top.probability || 0)));
  const severityClass = severityToClass(top.severity);

  result.innerHTML = `
    <article class="diagnostic-report-pro">
      <div class="report-topline">
        <div class="brand-lockup">
          <img class="report-brand-logo" src="${brandLogoSrc(vehicle.brand)}" onerror="this.src='/static/img/brands/default.svg'" alt="${escapeHtml(vehicle.brand || 'DZ Nova')} logo">
          <div>
            <span class="report-badge">${t.report}</span>
            <h2>${escapeHtml(vehicle.brand || '--')} ${escapeHtml(vehicle.model || '')}</h2>
            <p>${escapeHtml(vehicle.year || '--')} · ${escapeHtml(vehicle.fuel || '--')} · ${escapeHtml(vehicle.transmission || '--')} · ${escapeHtml(vehicle.mileage || '--')} km</p>
          </div>
        </div>
        <div class="health-ring" style="--score:${score}"><strong>${score}%</strong><span>${t.health}</span></div>
      </div>

      <div class="diagnostic-verdict ${severityClass}">
        <div>
          <span>${t.most}</span>
          <h3>${escapeHtml(top.fault || 'Unknown fault')}</h3>
          <p>${escapeHtml(data.chat_response || data.message || '')}</p>
        </div>
        <div class="probability-meter">
          <strong>${probability}%</strong>
          <span>${t.prob}</span>
          <div class="prob"><i style="width:${probability}%"></i></div>
        </div>
      </div>

      <div class="report-kpis">
        <div><span>${t.sev}</span><strong>${escapeHtml(top.severity || '--')}</strong></div>
        <div><span>${t.cat}</span><strong>${escapeHtml(top.category || '--')}</strong></div>
        <div><span>${t.obd}</span><strong>${escapeHtml(top.obd_codes || 'N/A')}</strong></div>
        <div><span>TF-IDF</span><strong>${escapeHtml(top.tfidf_score ?? '--')}%</strong></div>
        <div><span>Concepts</span><strong>${escapeHtml(top.concept_match ?? '--')}%</strong></div>
      </div>

      <div class="ai-explanation-grid">
        <section><h4>${t.exp}</h4><p>${escapeHtml(localizedDescription(top, lang))}</p></section>
        <section><h4>${t.rec}</h4><p>${escapeHtml(top.recommendation || '--')}</p></section>
      </div>

      <div class="service-workshop-card">
        <div class="service-icon">📍</div>
        <div>
          <h4>${t.workshopTitle}</h4>
          <p>${t.workshopText}</p>
          <small>${t.workshopHint}</small>
        </div>
        <button type="button" class="btn btn-primary" onclick="findNearbyWorkshops()">${t.workshopBtn}</button>
      </div>

      <div class="result-tools"><button type="button" class="btn btn-primary" onclick="exportPDF()">🧾 ${t.pdf}</button></div>
    </article>

    <section class="alternative-results">
      ${results.map((item, index) => resultCard(item, index, t, lang)).join('')}
    </section>
  `;
}

function resultCard(item, index, t, lang) {
  const probability = Math.max(0, Math.min(100, Number(item.probability || 0)));
  const description = localizedDescription(item, lang);
  const severityClass = severityToClass(item.severity);
  const title = index === 0 ? t.most : `${t.alt} #${index}`;
  const why = lang === 'ar'
    ? 'تم ترتيب هذه النتيجة اعتمادًا على تشابه الأعراض، شدة العطل، ومعلومات السيارة المخزنة في حساب المستخدم.'
    : lang === 'fr'
      ? 'Ce résultat est classé selon la similarité des symptômes, la gravité et le profil véhicule sauvegardé.'
      : 'This result is ranked using symptom similarity, severity, and the saved vehicle profile.';

  return `
    <article class="fault-card-pro ${severityClass}">
      <div class="fault-card-head">
        <span class="rank-chip">${title}</span>
        <span class="severity-chip">${escapeHtml(item.severity || '--')}</span>
      </div>
      <h3>${escapeHtml(item.fault || 'Unknown fault')}</h3>
      <div class="fault-progress"><span style="width:${probability}%"></span></div>
      <div class="fault-meta">
        <div><small>${t.prob}</small><strong>${probability}%</strong></div>
        <div><small>${t.cat}</small><strong>${escapeHtml(item.category || '--')}</strong></div>
        <div><small>${t.obd}</small><strong>${escapeHtml(item.obd_codes || 'N/A')}</strong></div>
      </div>
      <p><strong>${t.exp}:</strong> ${escapeHtml(description)}</p>
      <p><strong>${t.rec}:</strong> ${escapeHtml(item.recommendation || '--')}</p>
      <p class="muted"><strong>${t.why}</strong> ${why}</p>
    </article>
  `;
}

function localizedDescription(item, lang){
  return lang === 'ar'
    ? (item.arabic_description || item.description || '')
    : (item.description || item.arabic_description || '');
}

function severityToClass(severity=''){
  const s = String(severity).toLowerCase();
  if (s.includes('high') || s.includes('critical') || s.includes('élev') || s.includes('عالي') || s.includes('حرج')) return 'severity-high';
  if (s.includes('medium') || s.includes('moy') || s.includes('متوسط')) return 'severity-medium';
  return 'severity-low';
}

function findNearbyWorkshops() {
  const lang = document.documentElement.lang || localStorage.getItem('diagcar_lang') || 'en';
  const t = RESULT_I18N[lang] || RESULT_I18N.en;

  if (!navigator.geolocation) {
    alert(t.workshopNoGeo);
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;
      const queryByLang = lang === 'ar'
        ? 'ورشة تصليح سيارات'
        : lang === 'fr'
          ? 'garage réparation automobile'
          : 'car repair workshop';
      const url = `https://www.google.com/maps/search/${encodeURIComponent(queryByLang)}/@${lat},${lng},14z`;
      window.open(url, '_blank', 'noopener');
    },
    () => alert(t.workshopDenied),
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
  );
}

function exportPDF() {
  const content = document.getElementById('result')?.innerHTML || '';
  const lang = document.documentElement.lang || 'en';
  const dir = lang === 'ar' ? 'rtl' : 'ltr';
  const w = window.open('', '_blank');
  if (!w) return;

  w.document.write(`<!doctype html><html lang="${lang}" dir="${dir}"><head><meta charset="utf-8"><title>DZ Nova Diagnostic Report</title><style>
    body{font-family:Arial,Helvetica,sans-serif;padding:30px;color:#111;background:#fff;direction:${dir};text-align:${dir === 'rtl' ? 'right' : 'left'}}
    .result-card{border:1px solid #ccc;padding:20px;margin-bottom:20px;border-radius:10px;break-inside:avoid}.badge,.btn{display:none}.health-grid,.result-grid-compact{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.mini-card,.health-box{border:1px solid #ddd;padding:10px;border-radius:6px}.prob{height:10px;background:#eee;border-radius:20px;overflow:hidden}.prob span,.prob i,.fault-progress span{display:block;height:100%;background:#f5b301}.muted{color:#555}@media print{body{padding:15px}}
  </style></head><body>${content}</body></html>`);
  w.document.close();
  w.onload = () => { w.focus(); w.print(); };
}

function healthScore(item) {
  const probability = Number(item?.probability || 0);
  const severity = String(item?.severity || '').toLowerCase();
  let penalty = probability * 0.45;
  if (severity.includes('critical') || severity.includes('crit') || severity.includes('حرج')) penalty += 30;
  else if (severity.includes('high') || severity.includes('élev') || severity.includes('عالي')) penalty += 20;
  else penalty += 10;
  return Math.max(8, Math.round(100 - penalty));
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;'
  }[char]));
}

if (voiceBtn) {
  voiceBtn.addEventListener('click', () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const lang = localStorage.getItem('diagcar_lang') || 'en';
    if (!SpeechRecognition) {
      alert(lang === 'ar' ? 'التعرف الصوتي غير مدعوم في هذا المتصفح. استعمل Chrome.' : lang === 'fr' ? 'La reconnaissance vocale n’est pas prise en charge. Utilisez Chrome.' : 'Voice recognition is not supported in this browser. Use Chrome.');
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = lang === 'ar' ? 'ar-DZ' : lang === 'fr' ? 'fr-FR' : 'en-US';
    recognition.interimResults = false;
    recognition.onstart = () => { voiceBtn.textContent = lang === 'ar' ? '🎙 جاري الاستماع...' : lang === 'fr' ? '🎙 Écoute...' : '🎙 Listening...'; };
    recognition.onend = () => { voiceBtn.textContent = lang === 'ar' ? '🎙 صوت' : lang === 'fr' ? '🎙 Voix' : '🎙 Voice'; };
    recognition.onresult = (event) => {
      symptoms.value += `${symptoms.value ? ' ' : ''}${event.results[0][0].transcript}`;
    };
    recognition.start();
  });
}
