from __future__ import annotations

import time

from .incidents import STATE

CORPUS = {
    "action": [
        "The Dark Knight (2008) - A gritty superhero movie about Batman facing the Joker.",
        "Mad Max: Fury Road (2015) - A high-octane chase across a post-apocalyptic wasteland.",
        "Die Hard (1988) - An NYPD officer tries to save his wife and others taken hostage by German terrorists."
    ],
    "comedy": [
        "Superbad (2007) - Two co-dependent high school seniors are forced to deal with separation anxiety.",
        "The Grand Budapest Hotel (2014) - A legendary concierge at a famous European hotel.",
        "Palm Springs (2020) - Two wedding guests stuck in a time loop."
    ],
    "sci-fi": [
        "Inception (2010) - A thief who steals corporate secrets through the use of dream-sharing technology.",
        "The Matrix (1999) - A computer hacker learns from mysterious rebels about the true nature of his reality.",
        "Interstellar (2014) - A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."
    ],
}


def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    
    # Keyword mapping for Vietnamese
    if "hành động" in lowered or "action" in lowered:
        return CORPUS["action"]
    if "hài" in lowered or "comedy" in lowered:
        return CORPUS["comedy"]
    if "khoa học viễn tưởng" in lowered or "sci-fi" in lowered:
        return CORPUS["sci-fi"]
        
    return ["No domain document matched. Use general fallback answer."]