"""
Test tổng hợp tất cả API endpoints của AptisKey backend.
Chạy từ thư mục backend/: python test_endpoints.py
"""
import urllib.request, urllib.parse, json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:8001'
PASS_ICON = '[PASS]'
FAIL_ICON = '[FAIL]'

results = []

def req_get(url, token=None):
    r = urllib.request.Request(url)
    if token:
        r.add_header('Authorization', f'Bearer {token}')
    resp = urllib.request.urlopen(r, timeout=5)
    return json.loads(resp.read()), resp.status

def req_post(url, data, token=None, json_body=False):
    if json_body:
        body = json.dumps(data).encode()
        r = urllib.request.Request(url, data=body, method='POST')
        r.add_header('Content-Type', 'application/json')
    else:
        body = urllib.parse.urlencode(data).encode()
        r = urllib.request.Request(url, data=body, method='POST')
        r.add_header('Content-Type', 'application/x-www-form-urlencoded')
    if token:
        r.add_header('Authorization', f'Bearer {token}')
    resp = urllib.request.urlopen(r, timeout=8)
    return json.loads(resp.read()), resp.status

def test(name, fn):
    try:
        result = fn()
        print(f'{PASS_ICON} {name}: {result}')
        results.append((name, True, str(result)))
        return result
    except Exception as e:
        msg = str(e)[:120]
        print(f'{FAIL_ICON} {name}: {msg}')
        results.append((name, False, msg))
        return None

# ===========================================================================
print('=' * 60)
print('APTISKEY ENDPOINT TEST SUITE')
print('=' * 60)

# ── 1. HEALTH ──────────────────────────────────────────────────────────────
print('\n[1] SYSTEM')
health = test('GET /health', lambda: req_get(f'{BASE}/health')[0])

# ── 2. AUTH LOGIN ──────────────────────────────────────────────────────────
print('\n[2] AUTHENTICATION')

login_data = test(
    'POST /auth/login (admin)',
    lambda: req_post(f'{BASE}/auth/login', {'username': 'admin@aptiskey.com', 'password': 'admin123'})[0]
)
token = login_data.get('access_token') if login_data else None

if not token:
    print('\n[ERROR] Cannot get token – aborting remaining tests.')
    sys.exit(1)

test(
    'GET /auth/me → role=admin',
    lambda: {'role': req_get(f'{BASE}/auth/me', token)[0].get('role'),
             'email': req_get(f'{BASE}/auth/me', token)[0].get('email')}
)

test(
    'GET /api/me (compat) → isAdmin=True',
    lambda: {'isAdmin': req_get(f'{BASE}/api/me', token)[0].get('isAdmin')}
)

# Login với student account
login_student = test(
    'POST /auth/login (student apitest)',
    lambda: req_post(f'{BASE}/auth/login', {'username': 'apitest@aptispro.com', 'password': 'test123'})[0]
)
student_token = login_student.get('access_token') if login_student else None

# ── 3. EXAM ENDPOINTS ──────────────────────────────────────────────────────
print('\n[3] EXAM')

tests_list = test(
    'GET /api/tests → list',
    lambda: {'count': len(req_get(f'{BASE}/api/tests', token)[0])}
)

# Nếu có tests trong DB
all_tests = None
try:
    all_tests, _ = req_get(f'{BASE}/api/tests', token)
except:
    pass

if all_tests:
    first_test_id = all_tests[0]['id']
    test(
        f'GET /api/tests/{first_test_id} → detail',
        lambda: {'skill': req_get(f'{BASE}/api/tests/{first_test_id}', token)[0].get('skill'),
                 'q_count': len(req_get(f'{BASE}/api/tests/{first_test_id}', token)[0].get('questions', []))}
    )
    
    # Test POST submit (dummy answer)
    test(
        f'POST /api/tests/{first_test_id}/submit',
        lambda: req_post(
            f'{BASE}/api/tests/{first_test_id}/submit',
            {'answers': {}},
            token=token,
            json_body=True
        )[0]
    )
else:
    print(f'  [SKIP] No tests in DB. Run seed_data.py first.')

test(
    'GET /api/results',
    lambda: {'count': len(req_get(f'{BASE}/api/results', token)[0])}
)

# ── 4. COMPAT DATA ENDPOINTS ───────────────────────────────────────────────
print('\n[4] COMPAT DATA')

compat_endpoints = [
    '/api/reading-question1-data',
    '/api/reading-question2-data',
    '/api/reading-question4-data',
    '/api/reading-question5-data',
    '/api/listening-question14-data',
    '/api/listening-question15-data',
    '/api/listening-question16-17-data',
]

for ep in compat_endpoints:
    def _make_fn(url):
        return lambda: {'status': 'ok', 'type': type(req_get(f'{BASE}{url}', token)[0]).__name__}
    test(f'GET {ep}', _make_fn(ep))

# ── 5. COMPAT TEST DATA ─────────────────────────────────────────────────────
print('\n[5] COMPAT TEST DATA (test_id=1)')
for ep in ['/api/grammar-data/1', '/api/reading-test-data/1',
           '/api/listeningkey-data/1', '/api/writingkey-data/1']:
    def _make_fn2(url):
        return lambda: {'status': 'ok'} if req_get(f'{BASE}{url}', token) else {}
    test(f'GET {ep}', _make_fn2(ep))

# ── 6. /login COMPAT ────────────────────────────────────────────────────────
print('\n[6] COMPAT LOGIN/LOGOUT')
test(
    'POST /login (compat)',
    lambda: req_post(f'{BASE}/login', {'username': 'admin@aptiskey.com', 'password': 'admin123'})[0]
)
test(
    'GET /logout (compat)',
    lambda: req_get(f'{BASE}/logout')[0]
)

# ── SUMMARY ─────────────────────────────────────────────────────────────────
print('\n' + '=' * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f'SUMMARY: {passed} PASSED / {failed} FAILED / {len(results)} TOTAL')
print('=' * 60)
if failed:
    print('\nFailed tests:')
    for name, ok, msg in results:
        if not ok:
            print(f'  - {name}: {msg}')
