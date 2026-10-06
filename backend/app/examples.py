"""Synthetic example reviews (no real provider or customer text) — the same set the Streamlit analyzer offers."""

EXAMPLES = [
    {"id": "overcharged", "label": "Overcharged", "kind": "complaint",
     "text": "The technician was three hours late, charged more than the quote, and the repair failed again two days later."},
    {"id": "no-show", "label": "No-show", "kind": "complaint",
     "text": "They never showed for the scheduled appointment. I called four times and they never called back. "
             "When someone finally answered, the manager was very rude and unprofessional."},
    {"id": "property-damage", "label": "Property damage", "kind": "complaint",
     "text": "After the water heater install we found water damage under the cabinet. The company refused to fix it "
             "and said it was not under warranty. Completely dishonest experience."},
    {"id": "on-time", "label": "On time", "kind": "positive",
     "text": "The team arrived on time, explained the work clearly, and finished the installation professionally."},
    {"id": "follow-up", "label": "Great follow-up", "kind": "positive",
     "text": "Fair price, honest estimate, and the owner checked in a week later to make sure everything was still working. "
             "Highly recommend them for any plumbing job."},
]
