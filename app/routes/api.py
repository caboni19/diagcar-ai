from flask import Blueprint, request, jsonify, session
import json, datetime
from app.services.ai_engine import diagnose, train_model

api_bp = Blueprint('api', __name__)

# ─── /api/diagnose ────────────────────────────────────────────────────────────
@api_bp.route('/diagnose', methods=['POST'])
def api_diagnose():
    data    = request.get_json(silent=True) or {}
    text    = (data.get('text') or '').strip()
    vehicle = data.get('vehicle') or {}
    lang    = data.get('lang', '')

    user = session.get('user') or {}
    saved_vehicle = {
        'brand':        user.get('car_brand',''),
        'model':        user.get('car_model',''),
        'year':         user.get('car_year',''),
        'fuel':         user.get('fuel_type',''),
        'transmission': user.get('transmission',''),
        'mileage':      user.get('mileage',''),
    }
    vehicle = {**saved_vehicle, **{k:v for k,v in vehicle.items() if v}}

    # ── Multi-turn memory: accumulate conversation context ──
    history = session.get('diag_history', [])
    if text:
        history.append({'role':'user','text':text,
                        'ts': datetime.datetime.utcnow().isoformat()})

    # Build enriched query combining last 3 turns
    combined_text = ' '.join(
        h['text'] for h in history[-3:] if h['role']=='user'
    ) if history else text

    result = diagnose(combined_text, vehicle=vehicle, lang=lang)
    result['vehicle'] = vehicle
    result['conversation_turns'] = len(history)

    # Store AI response in history
    if result.get('results'):
        top = result['results'][0]
        history.append({'role':'assistant',
                        'text': top.get('fault',''),
                        'probability': top.get('probability',0),
                        'ts': datetime.datetime.utcnow().isoformat()})
    session['diag_history'] = history[-20:]  # keep last 20 turns
    session.modified = True

    # Persist to DB
    try:
        from app.utils.db import execute
        if user and result.get('results'):
            top = result['results'][0]
            execute(
                'INSERT INTO diagnostics(user_id,input_text,vehicle_snapshot,'
                'top_fault,probability,severity,obd_codes,recommendation) '
                'VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
                (user.get('id'), text, json.dumps(vehicle, ensure_ascii=False),
                 top.get('fault'), top.get('probability'),
                 top.get('severity'), top.get('obd_codes'),
                 top.get('recommendation')),
            )
    except Exception as e:
        pass

    return jsonify(result)


# ─── /api/reset-conversation ─────────────────────────────────────────────────
@api_bp.route('/reset-conversation', methods=['POST'])
def reset_conversation():
    session.pop('diag_history', None)
    session.modified = True
    return jsonify({'success': True, 'message': 'Conversation reset.'})


# ─── /api/history ─────────────────────────────────────────────────────────────
@api_bp.route('/history')
def history():
    user = session.get('user')
    if not user:
        return jsonify([])
    try:
        from app.utils.db import fetch_all
        rows = fetch_all(
            'SELECT * FROM diagnostics WHERE user_id=%s ORDER BY created_at DESC LIMIT 30',
            (user['id'],)
        )
        return jsonify(rows or [])
    except Exception:
        return jsonify([])


# ─── /api/stats ───────────────────────────────────────────────────────────────
@api_bp.route('/stats')
def stats():
    user = session.get('user')
    if not user:
        return jsonify({})
    try:
        from app.utils.db import fetch_all, fetch_one
        rows = fetch_all(
            'SELECT severity, COUNT(*) as cnt FROM diagnostics '
            'WHERE user_id=%s GROUP BY severity', (user['id'],)
        )
        total = fetch_one(
            'SELECT COUNT(*) as total FROM diagnostics WHERE user_id=%s',
            (user['id'],)
        )
        sys_rows = fetch_all(
            'SELECT top_fault, COUNT(*) as cnt FROM diagnostics '
            'WHERE user_id=%s GROUP BY top_fault ORDER BY cnt DESC LIMIT 5',
            (user['id'],)
        )
        return jsonify({
            'by_severity': {r['severity']: r['cnt'] for r in (rows or [])},
            'total': (total or {}).get('total', 0),
            'top_faults': [{'fault': r['top_fault'], 'count': r['cnt']}
                           for r in (sys_rows or [])],
        })
    except Exception:
        return jsonify({'total': 0, 'by_severity': {}, 'top_faults': []})


# ─── /api/obd ─────────────────────────────────────────────────────────────────
@api_bp.route('/obd/<code>')
def obd_lookup(code):
    from app.services.ai_diagnostic_engine import OBD_ENRICHMENT, _get_engine
    code = code.upper().strip()
    # Direct enrichment dict
    if code in OBD_ENRICHMENT:
        d = OBD_ENRICHMENT[code]
        return jsonify({'found': True, 'code': code, **d})
    # Search in cases
    e = _get_engine()
    matches = [c for c in e.cases if code in str(c.get('codes_obd',''))]
    if matches:
        c = matches[0]
        return jsonify({
            'found': True, 'code': code,
            'nom_francais': c.get('nom_francais'),
            'categorie': c.get('categorie'),
            'description_arabe': c.get('description_arabe'),
            'action_recommandee': c.get('action_recommandee'),
            'niveau_gravite': c.get('niveau_gravite'),
        })
    return jsonify({'found': False, 'code': code,
                    'message': 'Code not found in database.'})


# ─── /api/retrain ─────────────────────────────────────────────────────────────
@api_bp.route('/retrain', methods=['POST'])
def retrain():
    train_model(force=True)
    return jsonify({'success': True, 'message': 'Knowledge base refreshed.'})


# ─── /api/engine-info ─────────────────────────────────────────────────────────
@api_bp.route('/engine-info')
def engine_info():
    try:
        from app.services.ai_diagnostic_engine import _get_engine
        e = _get_engine()
        return jsonify({
            'name': 'DiagCar Real AI Engine v4.1',
            'cases': len(e.cases),
            'vocab': len(e.idf_dict),
            'accuracy_avg': '55.7%',
            'layers': ['NLP+Stemmer+Spell','TF-IDF ML',
                       'Cosine+Attention Classification',
                       'Softmax DL Scoring'],
            'built': e._built,
        })
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500
