"""TF-IDF + LR classical floor pipeline (per ADR-017 + ADR-044 Q3).

Rung 0 of the trained-rung slate. Restores the SPEC §2 line 121 common-pattern
linear-features baseline that ADR-007 omitted; ADR-017 added it back.
Provides the only fully ``verified_disjoint`` contamination-state anchor in
the rung slate (trained on our LODO splits by construction; no possibility of
pretrain contamination).

Public API
----------
- ``build_tfidf_lr_pipeline(seed, tfidf_cfg, lr_cfg)`` -> sklearn ``Pipeline``
  implementing the locked recipe (TF-IDF FeatureUnion -> LogisticRegression).
"""

from __future__ import annotations

from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline


def build_tfidf_lr_pipeline(
    *,
    seed: int,
    tfidf_cfg: dict[str, Any],
    lr_cfg: dict[str, Any],
) -> Pipeline:
    """Build the locked TF-IDF + LR pipeline.

    Parameters
    ----------
    seed : int
        Random seed for ``LogisticRegression`` (per ADR-044 Q1, one of
        ``(42, 43, 44)``).
    tfidf_cfg : dict
        Parsed from ``configs/rungs/classical_floor.yaml`` ``tfidf`` section.
        Required keys: ``word_ngram_min``, ``word_ngram_max``,
        ``word_max_features``, ``char_ngram_min``, ``char_ngram_max``,
        ``char_max_features``, ``sublinear_tf``, ``lowercase``,
        ``strip_accents``.
    lr_cfg : dict
        Parsed from ``configs/rungs/classical_floor.yaml``
        ``logistic_regression`` section. Required keys: ``solver``, ``C``,
        ``class_weight``, ``max_iter``.

    Returns
    -------
    sklearn.pipeline.Pipeline
        ``FeatureUnion(word_tfidf + char_tfidf) -> LogisticRegression``.

    Notes
    -----
    The word analyzer uses default ``"word"`` (whitespace tokenization +
    Unicode-aware splitting). The char analyzer uses ``"char_wb"`` (character
    n-grams within word boundaries), which captures URL-encoded + base64 +
    delimiter attack patterns better than raw ``"char"`` while remaining
    interpretable. Both choices follow standard sklearn text-classification
    recipes; ADR-017 does not specifically lock the analyzer flavor.
    """
    word_tfidf = TfidfVectorizer(
        analyzer="word",
        ngram_range=(tfidf_cfg["word_ngram_min"], tfidf_cfg["word_ngram_max"]),
        max_features=tfidf_cfg["word_max_features"],
        sublinear_tf=tfidf_cfg["sublinear_tf"],
        lowercase=tfidf_cfg["lowercase"],
        strip_accents=tfidf_cfg["strip_accents"],
    )
    char_tfidf = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(tfidf_cfg["char_ngram_min"], tfidf_cfg["char_ngram_max"]),
        max_features=tfidf_cfg["char_max_features"],
        sublinear_tf=tfidf_cfg["sublinear_tf"],
        lowercase=tfidf_cfg["lowercase"],
        strip_accents=tfidf_cfg["strip_accents"],
    )
    features = FeatureUnion(
        [
            ("word", word_tfidf),
            ("char", char_tfidf),
        ]
    )
    classifier = LogisticRegression(
        solver=lr_cfg["solver"],
        C=lr_cfg["C"],
        class_weight=lr_cfg["class_weight"],
        max_iter=lr_cfg["max_iter"],
        random_state=seed,
    )
    return Pipeline(
        [
            ("features", features),
            ("classifier", classifier),
        ]
    )
