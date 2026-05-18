import logging
from functools import lru_cache

import anthropic
from fastapi import Depends, HTTPException, status

from app.core.config import settings
from app.schemas.session import AnalyzeRequest

logger = logging.getLogger(__name__)



class AnalyzeService:
    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def _build_system_prompt(self, request: AnalyzeRequest) -> str:
        prenom = request.prenom or "vous"
        progression_ctx = ""
        if request.last_score is not None:
            progression_ctx = (
                f"DERNIÈRE ANALYSE ({prenom.upper()}) : {request.last_score}/100\n"
                "→ Commence ton analyse par une phrase courte comparant ce score avec celui d'aujourd'hui.\n\n"
            )

        has_last_score = request.last_score is not None
        return (
            "Tu es Nicolas Mel, expert en prise de parole pour l'organisme Silence. "
            "Tu parles DIRECTEMENT à la personne, à la PREMIÈRE PERSONNE ('Je te recommande...', 'Mon conseil...'). "
            "Analyse avec BIENVEILLANCE. Mots BANNIS : faible, manque, mauvais, insuffisant, problème, défaut.\n\n"
            "RÈGLES IMPORTANTES :\n"
            f"- Commence TOUJOURS l'analyse par : 'Bonjour {prenom},'\n"
            "- Toutes les évaluations sont sur 100 (jamais sur 20).\n"
            "- Utilise TOUJOURS le mot 'accroche' à la place de 'hook'.\n"
            "- Ne mentionne JAMAIS les photos, images, captures ou frames. "
            "Présente les observations visuelles comme si tu regardais la personne en direct.\n\n"
            + progression_ctx
            + f"STRUCTURE :\n# 👋 Bonjour {prenom}\n"
            f"[Salutation personnalisée"
            f"{' + comparaison avec la dernière analyse' if has_last_score else ''}]\n\n"
            "# 📝 Retranscription complète\n[Retranscription intégrale]\n\n"
            "# 📊 Tableau de bord\nBarres [████████░░] 10 chars.\n"
            "**Non Verbale** : Regard / Posture / Gestuelle / Sourire\n"
            "**Para-Verbale** : Volume / Articulation / Silences / Débit\n"
            "**Verbale** : Structure / Rhétorique / Clarté\n\n"
            "# 🎯 Grille d'évaluation\n3 tableaux : Paramètre | Score /100 | Points Forts | Axes (commence par 'Je te recommande de...')\n\n"
            "# 🔍 Analyses complémentaires\n### Vitesse\n### Silences\n### Mots à accentuer\n"
            "### Vocabulaire émotionnel\n### Mots répétés\n### Sons de remplissage\n### Termes familiers\n\n"
            "# 🚀 Plan d'action\n| Priorité | Objectif | Exercice |\n[3 objectifs, exercices : 'Je te propose de...']\n\n"
            "# 🏆 Score final\n**Score global : XX/100**\nPhrase de contextualisation."
        )

    def analyze(self, request: AnalyzeRequest) -> str:
        audio = request.audio_stats
        visual = request.visual_stats
        vl = lambda v: "discret" if v < 25 else "présent" if v < 50 else "très engagé" if v < 75 else "excellent"

        system_prompt = self._build_system_prompt(request)

        context_text = (
            f"Type : {request.type_discours_label}\nDurée : {request.duree_min} min\n\n"
            f"=== RETRANSCRIPTION ===\n{request.transcript}\n\n"
        )
        if audio:
            context_text += (
                f"DONNÉES :\n- Durée : {audio.get('duree_sec', 0)}s\n"
                f"- Mots : {audio.get('wc', 0)}\n"
                f"- Débit : {audio.get('debit', 'non mesuré')}\n"
                f"- Volume : {audio.get('volume', 'non mesuré')}\n"
            )
        if visual:
            context_text += (
                f"\nINDICATEURS VISUELS :\n"
                f"- Regard : {vl(visual.get('regard', 0))}\n"
                f"- Posture : {vl(visual.get('posture', 0))}\n"
                f"- Gestuelle : {vl(visual.get('gestuelle', 0))}\n"
                f"- Sourire : {vl(visual.get('sourire', 0))}\n"
            )

        content = [
            *[
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img}}
                for img in request.images[:4]
            ],
            {"type": "text", "text": context_text},
        ]

        logger.info("Analyse démarrée : type=%s, modèle=%s", request.type_discours, settings.MODEL_NAME)
        try:
            response = self.client.messages.create(
                model=settings.MODEL_NAME,
                max_tokens=5000,
                system=system_prompt,
                messages=[{"role": "user", "content": content}],
            )
        except anthropic.RateLimitError:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Limite d'utilisation Anthropic atteinte. Réessayez dans quelques instants.",
            )
        except anthropic.APIConnectionError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Impossible de joindre l'API Anthropic. Vérifiez votre connexion.",
            )
        except anthropic.APIStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erreur API Anthropic : {e.message}",
            )

        logger.info("Analyse terminée : type=%s", request.type_discours)
        return response.content[0].text


@lru_cache()
def get_anthropic_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def get_analyze_service(
    client: anthropic.Anthropic = Depends(get_anthropic_client),
) -> AnalyzeService:
    return AnalyzeService(client)
