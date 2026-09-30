# ml — AI matching

`campusfind_ml/matching.py` scores how well a lost item matches found items (and vice versa).
It is plain Python + scikit-learn with no web or database code, so it is independent of the API.

- **TF-IDF cosine similarity** on the title and description
- **Exact-match attributes**: category, brand, colour, location
- **Date proximity**: linear decay over 14 days
- Weights: title 20%, description 25%, category 15%, brand 10%, colour 10%, location 10%, date 10%
- Candidates scoring below 50 are dropped. The result is a *match score*, not a probability.

The backend imports this package (`PYTHONPATH` includes `ml/`; the backend Docker image copies it in)
and exposes it at `GET /api/items/{item_id}/matches`. Not implemented: computer vision, deep
learning, sentence-transformers.
