// Parity test: the TypeScript port must reproduce Rithik's Python outputs (frontend/data/golden.json, written by
// scripts/export_frontend_data.py from artifacts/*.joblib and app/risk_logic.py).
import assert from "node:assert/strict";
import { test } from "node:test";
import golden from "../data/golden.json";
import { analyzeReview, scoreText } from "../lib/engine/analyze";
import { maskSensitiveAndLeakage } from "../lib/engine/text";

for (const g of golden) {
  test(`parity: ${g.text.slice(0, 48)}`, () => {
    const r = analyzeReview(g.text);
    assert.ok(Math.abs(scoreText(g.text) - g.raw_probability) < 1e-4, `probability ${scoreText(g.text)} vs ${g.raw_probability}`);
    assert.equal(r.risk_probability, g.risk_probability);
    assert.equal(r.management_attention, g.management_attention);
    assert.equal(r.primary_aspect, g.primary_aspect);
    assert.deepEqual(r.detected_aspects, g.detected_aspects);
    assert.deepEqual(r.matched_phrases, g.matched_phrases);
    assert.equal(r.recommended_action, g.recommended_action);
    assert.deepEqual(r.sentences.map((s) => s.text), g.sentences);
    r.sentences.forEach((s, i) => assert.ok(Math.abs((s.risk_probability ?? 0) - g.sentence_probabilities[i]) < 1e-3, `sentence ${i}`));
  });
}

test("masking hides phones, money and star phrases", () => {
  assert.equal(maskSensitiveAndLeakage("Call 520-555-1234, paid $900, gave one star"), "Call PHONETOKEN , paid MONEYTOKEN gave RATINGTOKEN");
});

test("token weights add up to the logit", () => {
  const w = analyzeReview("The technician was three hours late and charged more than the quote.").weights!;
  assert.ok(Math.abs(w.logit - (w.bias + w.explained_positive + w.explained_negative)) < 0.01);
});

test("empty text is rejected", () => {
  assert.throws(() => analyzeReview("   "));
});
