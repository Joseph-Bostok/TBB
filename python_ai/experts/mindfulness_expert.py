"""
Mindfulness and Meditation Expert

This module implements a mindfulness-focused expert that helps users with:
- Stress and overwhelm
- Difficulty being present
- Sleep problems and insomnia
- Physical tension and restlessness
- Difficulty focusing

Mindfulness Core Principles:
1. Present-moment awareness without judgment
2. Acceptance of thoughts and feelings without resistance
3. Mind-body connection and somatic awareness
4. Compassionate observation rather than control

Techniques Used:
- Breathing exercises
- Body scan meditation
- Grounding techniques
- Mindful awareness practices
- Progressive muscle relaxation
- Sleep hygiene guidance

IMPORTANT: This provides mindfulness guidance, NOT medical treatment.
Sleep problems may have medical causes requiring professional evaluation.
"""

import logging
import random
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MindfulnessExpert:
    """
    Mindfulness Expert for stress, overwhelm, and present-moment awareness

    This expert provides guided meditation exercises, breathing techniques,
    and mindfulness practices for managing stress and cultivating calm.
    """

    def __init__(self):
        """Initialize the Mindfulness expert with response templates"""

        # Opening responses that acknowledge distress
        self.acknowledgments = [
            "It sounds like you're carrying a lot right now.",
            "I hear that you're feeling overwhelmed. Let's take this moment to pause together.",
            "Thank you for sharing. Sometimes just acknowledging how we feel is the first step.",
            "It takes awareness to recognize when we need to slow down. You're already practicing mindfulness by noticing this.",
        ]

        # Breathing exercises
        self.breathing_exercises = [
            {
                "name": "4-7-8 Breathing (Relaxation Breath)",
                "purpose": "Activates your parasympathetic nervous system to promote calm",
                "instructions": (
                    "1. Exhale completely through your mouth\n"
                    "2. Close your mouth and breathe in through your nose for 4 counts\n"
                    "3. Hold your breath for 7 counts\n"
                    "4. Exhale completely through your mouth for 8 counts\n"
                    "5. Repeat 3-4 times\n\n"
                    "Why it works: The extended exhale signals your body to relax."
                )
            },
            {
                "name": "Box Breathing (Square Breathing)",
                "purpose": "Used by Navy SEALs to stay calm under pressure",
                "instructions": (
                    "Imagine tracing a square:\n"
                    "1. Breathe IN for 4 counts (first side)\n"
                    "2. HOLD for 4 counts (second side)\n"
                    "3. Breathe OUT for 4 counts (third side)\n"
                    "4. HOLD for 4 counts (fourth side)\n"
                    "5. Repeat for 2-5 minutes\n\n"
                    "Why it works: Equal counts create rhythmic balance in your nervous system."
                )
            },
            {
                "name": "Belly Breathing (Diaphragmatic Breathing)",
                "purpose": "Shifts from shallow chest breathing to deep, calming breaths",
                "instructions": (
                    "1. Place one hand on your chest, one on your belly\n"
                    "2. Breathe in slowly through your nose\n"
                    "3. Your belly hand should rise more than your chest hand\n"
                    "4. Exhale slowly through your mouth\n"
                    "5. Continue for 5-10 minutes\n\n"
                    "Why it works: Engages your diaphragm, which is linked to the calming vagus nerve."
                )
            },
            {
                "name": "5-5-5 Simple Breath",
                "purpose": "Quick, accessible technique for immediate stress relief",
                "instructions": (
                    "1. Breathe in through your nose for 5 counts\n"
                    "2. Hold for 5 counts\n"
                    "3. Breathe out through your mouth for 5 counts\n"
                    "4. Repeat 5 times\n\n"
                    "Why it works: Slows your breath rate, signaling safety to your brain."
                )
            },
        ]

        # Grounding techniques for anxiety/overwhelm
        self.grounding_exercises = [
            {
                "name": "5-4-3-2-1 Grounding",
                "purpose": "Brings you back to the present moment using your senses",
                "instructions": (
                    "Notice and name:\n"
                    "- **5 things** you can **see** (a crack in the wall, a shadow, a color)\n"
                    "- **4 things** you can **touch** (your feet on the floor, your clothes, the air)\n"
                    "- **3 things** you can **hear** (traffic, breathing, a fan humming)\n"
                    "- **2 things** you can **smell** (or smells you enjoy)\n"
                    "- **1 thing** you can **taste** (gum, coffee, or focus on your mouth)\n\n"
                    "Why it works: Grounds you in sensory reality, interrupting anxious thoughts."
                )
            },
            {
                "name": "Physical Grounding",
                "purpose": "Uses physical sensations to anchor you in the present",
                "instructions": (
                    "- Press your feet firmly into the floor\n"
                    "- Notice the contact points: heels, balls of feet, toes\n"
                    "- Feel the solidity supporting you\n"
                    "- Imagine roots growing from your feet into the earth\n"
                    "- Take 5 deep breaths while maintaining this awareness\n\n"
                    "Why it works: Connects you to your body and the physical world."
                )
            },
            {
                "name": "Cold Water Grounding",
                "purpose": "Physiological interrupt for intense anxiety or panic",
                "instructions": (
                    "- Hold ice cubes in your hands\n"
                    "- OR splash cold water on your face\n"
                    "- OR run cold water over your wrists\n"
                    "- Focus completely on the sensation\n"
                    "- Notice: temperature, wetness, tingling\n\n"
                    "Why it works: Cold temperature activates the dive reflex, rapidly calming your nervous system."
                )
            },
        ]

        # Body scan meditation
        self.body_scan = {
            "name": "Body Scan Meditation",
            "purpose": "Releases physical tension and increases body awareness",
            "instructions": (
                "Find a comfortable position (sitting or lying down).\n\n"
                "We'll move through your body, noticing sensations without trying to change them:\n\n"
                "1. **Feet:** Notice your toes, the soles of your feet. Any tingling? Warmth? Tension?\n"
                "2. **Legs:** Move up to your calves, knees, thighs. Just observe.\n"
                "3. **Torso:** Notice your belly rising and falling with breath. Your chest. Your back.\n"
                "4. **Hands:** Feel your fingers, palms, wrists.\n"
                "5. **Arms:** Move up through your forearms, elbows, upper arms.\n"
                "6. **Shoulders:** Often hold tension. Just notice, don't fix.\n"
                "7. **Neck and throat:** Any tightness? Softness?\n"
                "8. **Face:** Jaw, cheeks, eyes, forehead. Let your face soften.\n"
                "9. **Whole body:** Sense your entire body as one. Notice the breath moving through you.\n\n"
                "Take your time with each area. This isn't about relaxing (though that may happen). "
                "It's about awareness.\n\n"
                "Why it works: Brings mind and body into connection, often releasing unconscious tension."
            )
        }

        # Sleep-specific guidance
        self.sleep_guidance = {
            "name": "Sleep Hygiene & Mindfulness for Insomnia",
            "content": (
                "**Mindfulness for Sleep:**\n\n"
                "The paradox: Trying to sleep keeps you awake. Instead, practice being awake restfully.\n\n"
                "**Techniques:**\n"
                "1. **Body Scan:** Systematically relax each body part (see body scan exercise)\n"
                "2. **Breath Counting:** Count each exhale up to 10, then start over. When your mind wanders, gently return to 1.\n"
                "3. **Accepting Wakefulness:** 'I'm awake right now, and that's okay. My body knows how to sleep when it's ready.'\n\n"
                "**Sleep Hygiene Basics:**\n"
                "- **Consistent schedule:** Same bedtime and wake time, even weekends\n"
                "- **Wind-down routine:** 30-60 minutes before bed doing calming activities\n"
                "- **Bed is for sleep:** Not for scrolling, worrying, or problem-solving\n"
                "- **20-minute rule:** If awake for 20+ minutes, get up and do something calming\n"
                "- **Limit screens:** Blue light disrupts melatonin; avoid 1 hour before bed\n"
                "- **Environment:** Cool, dark, quiet\n\n"
                "**If insomnia persists:** Consider seeing a sleep specialist or therapist trained in CBT-I "
                "(Cognitive Behavioral Therapy for Insomnia)."
            )
        }

        # Quick stress relief
        self.quick_techniques = [
            "**One Mindful Breath:** Stop right now. Take one full, deep breath. Notice the inhale, the pause, the exhale. That's it. You just practiced mindfulness.",
            "**Hand on Heart:** Place your hand on your heart. Feel it beating. This is your body working to keep you alive. Breathe into this awareness.",
            "**Soften and Soothe:** Notice where you're holding tension. Say to yourself: 'Soften' (let the tension melt), 'Soothe' (send kindness there), 'Allow' (let it be).",
            "**Three-Breath Reset:** Take three intentional breaths. Breath 1: Release tension. Breath 2: Arrive in this moment. Breath 3: Set your intention.",
        ]

        logger.info("Mindfulness Expert initialized")

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate a mindfulness-informed response

        Args:
            user_message: The user's current message
            conversation_history: Recent conversation for context
            context: Additional context (routing scores, user metadata, etc.)

        Returns:
            str: The mindfulness expert's response
        """

        message_lower = user_message.lower()

        # Detect primary concern
        is_stressed = any(word in message_lower for word in [
            'stressed', 'stress', 'overwhelmed', 'too much', 'burnout', 'exhausted'
        ])

        is_sleep = any(word in message_lower for word in [
            'sleep', 'insomnia', 'can\'t sleep', 'tired', 'restless', 'awake'
        ])

        is_anxious = any(word in message_lower for word in [
            'anxious', 'panic', 'racing', 'worried', 'nervous', 'tense'
        ])

        is_distracted = any(word in message_lower for word in [
            'focus', 'concentrate', 'distracted', 'scattered', 'mind wandering'
        ])

        needs_calm = any(word in message_lower for word in [
            'calm', 'relax', 'peace', 'quiet', 'still'
        ])

        # Build response
        response_parts = []

        # 1. Acknowledgment
        response_parts.append(random.choice(self.acknowledgments))

        # 2. Concern-specific intervention
        if is_sleep:
            response_parts.append(
                "\n\nSleep difficulties are so frustrating. When we can't sleep, we often try harder, "
                "which paradoxically keeps us awake. Mindfulness offers a different approach."
            )
            response_parts.append(f"\n\n{self.sleep_guidance['content']}")

        elif is_stressed or needs_calm:
            response_parts.append(
                "\n\nWhen we're stressed, our nervous system is in 'fight or flight' mode. "
                "Mindfulness and breathwork can shift us into 'rest and digest' mode."
            )
            response_parts.append("\n\n**Let's try a breathing exercise together:**\n")

            # Select a breathing exercise
            exercise = random.choice(self.breathing_exercises)
            response_parts.append(f"\n**{exercise['name']}**\n")
            response_parts.append(f"*{exercise['purpose']}*\n\n")
            response_parts.append(exercise['instructions'])

            response_parts.append(
                "\n\nTake your time with this. Even 2-3 minutes can make a difference."
            )

        elif is_anxious:
            response_parts.append(
                "\n\nWhen anxiety is high, our mind often goes to the past (regret) or future (worry). "
                "Grounding brings us back to the only moment we can actually inhabit: right now."
            )
            response_parts.append("\n\n**Let's practice a grounding technique:**\n")

            # Select a grounding exercise
            exercise = random.choice(self.grounding_exercises)
            response_parts.append(f"\n**{exercise['name']}**\n")
            response_parts.append(f"*{exercise['purpose']}*\n\n")
            response_parts.append(exercise['instructions'])

        elif is_distracted:
            response_parts.append(
                "\n\nDifficulty focusing is incredibly common. Our minds naturally wander - "
                "it's what minds do. Mindfulness isn't about stopping thoughts, but noticing when we've wandered and gently returning."
            )
            response_parts.append(
                "\n\n**Focused Attention Practice:**\n"
                "1. Choose one object: your breath, sounds, or a physical sensation\n"
                "2. Rest your attention there\n"
                "3. When you notice you've wandered (you will!), that's actually a win - you've become aware\n"
                "4. Gently return your focus\n"
                "5. Repeat 1000 times. Seriously - the practice IS the returning, not staying focused.\n\n"
                "Start with just 2 minutes. Each time you notice and return, you're strengthening your attention muscle."
            )

        else:
            # General mindfulness response
            response_parts.append(
                "\n\nMindfulness is about being present with whatever is here, without judgment. "
                "Not trying to feel better, but being willing to feel what's present."
            )
            response_parts.append(f"\n\n{random.choice(self.quick_techniques)}")
            response_parts.append("\n\n" + f"**{self.body_scan['name']}**\n")
            response_parts.append(f"*{self.body_scan['purpose']}*\n\n")
            response_parts.append(self.body_scan['instructions'])

        # 3. Closing invitation
        response_parts.append(
            "\n\nHow are you feeling right now, in this moment?"
        )

        # Combine all parts
        response = "".join(response_parts)

        logger.info(f"Mindfulness Expert generated response (length: {len(response)} chars)")
        return response

    def get_quick_exercise(self) -> str:
        """Return a random quick mindfulness technique"""
        return random.choice(self.quick_techniques)


# Global expert instance
mindfulness_expert = MindfulnessExpert()


def get_mindfulness_expert() -> MindfulnessExpert:
    """Get the global mindfulness expert instance"""
    return mindfulness_expert
