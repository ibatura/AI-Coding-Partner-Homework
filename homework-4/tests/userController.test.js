'use strict';

/**
 * Unit tests for getUserById in src/controllers/userController.js
 *
 * Covers the fix on line 19:
 *   Before: const userId = req.params.id;
 *   After:  const userId = parseInt(req.params.id, 10);
 *
 * The users array is module-local and not exported.
 * Tests call the exported function directly with mock req/res objects.
 */

const { getUserById } = require('../src/controllers/userController');

/**
 * Build a minimal mock Express response object.
 * Each method returns `this` so chaining (res.status(x).json(y)) works.
 */
function buildMockRes() {
  const res = {
    _status: null,
    _json: undefined,
    status(code) {
      this._status = code;
      return this;
    },
    json(data) {
      this._json = data;
      return this;
    }
  };
  return res;
}

/** Build a minimal mock Express request with a params.id value. */
function buildMockReq(id) {
  return { params: { id } };
}

// ---------------------------------------------------------------------------
// Happy path — valid numeric string ID returns the matching user
// ---------------------------------------------------------------------------

test('happy path — id "123" returns Alice Smith with HTTP 200 (no status call)', async () => {
  const req = buildMockReq('123');
  const res = buildMockRes();

  await getUserById(req, res);

  // No explicit status call means the default 200 is used; _status stays null.
  expect(res._status).toBeNull();
  expect(res._json).toEqual({ id: 123, name: 'Alice Smith', email: 'alice@example.com' });
});

test('happy path — id "456" returns Bob Johnson with HTTP 200 (no status call)', async () => {
  const req = buildMockReq('456');
  const res = buildMockRes();

  await getUserById(req, res);

  expect(res._status).toBeNull();
  expect(res._json).toEqual({ id: 456, name: 'Bob Johnson', email: 'bob@example.com' });
});

// ---------------------------------------------------------------------------
// Edge case — non-numeric ID (parseInt returns NaN, find returns undefined)
// ---------------------------------------------------------------------------

test('edge case — non-numeric id "abc" returns 404 with error body', async () => {
  const req = buildMockReq('abc');
  const res = buildMockRes();

  await getUserById(req, res);

  expect(res._status).toBe(404);
  expect(res._json).toEqual({ error: 'User not found' });
});

// ---------------------------------------------------------------------------
// Edge case — numeric-looking but non-existent ID
// ---------------------------------------------------------------------------

test('edge case — id "999" (no matching user) returns 404 with error body', async () => {
  const req = buildMockReq('999');
  const res = buildMockRes();

  await getUserById(req, res);

  expect(res._status).toBe(404);
  expect(res._json).toEqual({ error: 'User not found' });
});

// ---------------------------------------------------------------------------
// Regression — the original bug: string "123" must match numeric id 123
//
// Before the fix:
//   userId = req.params.id  =>  "123" (string)
//   users.find(u => u.id === "123")  =>  undefined  (strict equality fails)
//   response: 404 — User not found  (WRONG)
//
// After the fix:
//   userId = parseInt("123", 10)  =>  123 (number)
//   users.find(u => u.id === 123)  =>  { id: 123, ... }  (correct)
//   response: 200 with user object  (CORRECT)
// ---------------------------------------------------------------------------

test('regression — string "123" now matches numeric id 123 (pre-fix this returned 404)', async () => {
  const req = buildMockReq('123');
  const res = buildMockRes();

  await getUserById(req, res);

  // Must NOT return 404 (the pre-fix failure mode).
  expect(res._status).not.toBe(404);
  // Must return the user object, confirming parseInt resolved the type mismatch.
  expect(res._json).toHaveProperty('id', 123);
  expect(res._json).toHaveProperty('name', 'Alice Smith');
});
