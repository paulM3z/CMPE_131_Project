"""Tests for client-side translation coverage safeguards."""


def test_i18n_uses_google_fallback_for_text_and_attributes():
    script = open("app/static/js/i18n.js", encoding="utf-8").read()

    for lang in ["es", "fr", "de", "pt", "zh", "ja", "ko", "ar"]:
        assert f"{lang}:" in script
        assert f"{lang}: {{}}" not in script

    assert "translateWithGoogle(nodes)" in script
    assert "translateAttributesWithGoogle(attributes)" in script
    assert "[placeholder], [title], [aria-label], [alt], [value]" in script
    assert "translate.googleapis.com/translate_a/single" in script
    assert "break;" not in script
