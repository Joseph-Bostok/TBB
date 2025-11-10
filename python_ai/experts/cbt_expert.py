"""
Cognitive Behavioral Therapy (CBT) Expert

This module implements a CBT-focused therapy expert that helps users with:
- Anxiety and worry
- Depression and negative thoughts
- Cognitive distortions
- Thought challenging and reframing

CBT Core Principles:
1. Thoughts, feelings, and behaviors are interconnected
2. Negative thought patterns contribute to distress
3. Changing thoughts can change feelings and behaviors
4. Focus on present problems and practical solutions

Therapeutic Techniques Used:
- Socratic questioning
- Cognitive restructuring
- Thought records
- Behavioral activation
- Exposure principles

IMPORTANT: This is educational/supportive, NOT clinical therapy.
Users in crisis are directed to professional resources.
"""

import logging
import random
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ==================== CBT Response Patterns ====================

class CBTExpert:
    """
    CBT Expert for anxiety, depression, and negative thought patterns

    This expert uses rule-based responses organized by common CBT interventions.
    In production, this would be replaced with or augmented by LLM-based responses.

    Response Strategy:
    1. Validate the user's feelings (therapeutic alliance)
    2. Identify cognitive distortions if present
    3. Use Socratic questioning to challenge thoughts
    4. Offer coping strategies
    5. Provide psychoeducation
    """

    def __init__(self):
        """Initialize the CBT expert with response templates"""

        # Opening responses that validate feelings
        self.validations = [
            "I hear that you're going through a difficult time.",
            "Thank you for sharing that with me. It takes courage to talk about these feelings.",
            "What you're experiencing sounds really challenging.",
            "I appreciate you opening up about this.",
        ]

        # Socratic questions for exploring thoughts
        self.socratic_questions = [
            "What evidence do you have that supports this thought?",
            "What evidence contradicts this thought?",
            "Is there another way to look at this situation?",
            "What would you tell a friend who had this thought?",
            "How likely is it that your fear will actually happen?",
            "What's the worst that could happen? Could you cope with that?",
            "Are you confusing a thought with a fact?",
        ]

        # Coping strategies for anxiety
        self.anxiety_coping = [
            "**Grounding Exercise:** Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. This brings you back to the present moment.",
            "**Breathing Exercise:** Try the 4-7-8 technique: breathe in for 4 counts, hold for 7, exhale for 8. This activates your parasympathetic nervous system.",
            "**Thought Challenge:** Write down your worry. Then write down evidence for and against it. Often we'll find our fears are more extreme than reality.",
            "**Worry Time:** Set aside 15 minutes to worry. When anxious thoughts come outside this time, remind yourself you'll address them during worry time. This contains anxiety.",
        ]

        # Coping strategies for depression
        self.depression_coping = [
            "**Behavioral Activation:** Even when you don't feel like it, try one small pleasant activity. Depression tells us we won't enjoy things, but action often improves mood.",
            "**Activity Scheduling:** Plan one thing you used to enjoy and commit to doing it, even for just 10 minutes. Note your mood before and after.",
            "**Break It Down:** Overwhelming tasks paralyze us. Break your goal into the smallest possible step. What's one tiny thing you could do today?",
            "**Self-Compassion:** Notice how harshly you're talking to yourself. Would you speak to a friend this way? Try offering yourself the same kindness.",
        ]

        # Common cognitive distortions and their explanations
        self.distortions = {
            "catastrophizing": {
                "description": "Imagining the worst possible outcome",
                "example": "If I fail this test, my life will be ruined",
                "challenge": "What's more likely to happen? What evidence is this based on?",
            },
            "all_or_nothing": {
                "description": "Thinking in extremes with no middle ground",
                "example": "If I'm not perfect, I'm a total failure",
                "challenge": "Can both be partially true? Where are you on the spectrum between these extremes?",
            },
            "overgeneralization": {
                "description": "Drawing broad conclusions from single events",
                "example": "I failed once, so I'll always fail",
                "challenge": "Is this always true? Can you think of counter-examples?",
            },
            "mind_reading": {
                "description": "Assuming you know what others think",
                "example": "Everyone thinks I'm stupid",
                "challenge": "Do you have evidence for this? Could there be other explanations?",
            },
            "should_statements": {
                "description": "Rigid rules about how you or others should behave",
                "example": "I should be better at this by now",
                "challenge": "Says who? What's a more flexible, compassionate way to think about this?",
            },
        }

        logger.info("CBT Expert initialized")

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate a CBT-informed response

        This uses pattern matching and heuristics to provide appropriate responses.
        In production, this would use an LLM with CBT-specific prompting.

        Args:
            user_message: The user's current message
            conversation_history: Recent conversation for context
            context: Additional context (routing scores, user metadata, etc.)

        Returns:
            str: The CBT expert's response

        Response Construction:
        1. Start with validation
        2. Identify the primary concern (anxiety, depression, etc.)
        3. Provide relevant intervention
        4. End with a question or action item
        """

        message_lower = user_message.lower()

        # Detect primary concern
        is_anxiety = any(word in message_lower for word in [
            'anxious', 'anxiety', 'worry', 'worried', 'panic', 'nervous', 'fear', 'scared'
        ])

        is_depression = any(word in message_lower for word in [
            'depressed', 'depression', 'hopeless', 'worthless', 'sad', 'empty', 'numb'
        ])

        is_overthinking = any(word in message_lower for word in [
            'overthinking', 'ruminating', 'can\'t stop thinking', 'racing thoughts', 'spiraling'
        ])

        is_self_critical = any(word in message_lower for word in [
            'failure', 'not good enough', 'stupid', 'useless', 'hate myself', 'disappointed in myself'
        ])

        # Build response
        response_parts = []

        # 1. Validation (therapeutic alliance)
        response_parts.append(random.choice(self.validations))

        # 2. Concern-specific intervention
        if is_anxiety:
            response_parts.append(
                "\n\nAnxiety often involves our mind predicting negative outcomes that may not happen. "
                "Let's examine these thoughts together."
            )
            response_parts.append(f"\n\n{random.choice(self.socratic_questions)}")
            response_parts.append(f"\n\n{random.choice(self.anxiety_coping)}")

        elif is_depression:
            response_parts.append(
                "\n\nDepression can make everything feel heavy and hopeless. "
                "It's important to remember that these feelings, while real, don't reflect the complete reality."
            )
            response_parts.append(
                f"\n\nOne of the hardest things about depression is the loss of motivation. "
                f"In CBT, we've found that **action often precedes motivation**, not the other way around."
            )
            response_parts.append(f"\n\n{random.choice(self.depression_coping)}")

        elif is_overthinking:
            response_parts.append(
                "\n\nRacing thoughts and rumination are exhausting. When we get stuck in thought loops, "
                "we're usually trying to solve a problem that can't be solved through thinking alone."
            )
            response_parts.append(
                "\n\n**Technique - Thought Defusion:** Instead of 'I'm worthless', try 'I'm having the thought that I'm worthless.' "
                "This creates distance between you and your thoughts. You are not your thoughts."
            )
            response_parts.append(f"\n\n{random.choice(self.socratic_questions)}")

        elif is_self_critical:
            response_parts.append(
                "\n\nIt sounds like you're being very hard on yourself. Self-criticism often comes from trying to protect ourselves, "
                "but it usually makes us feel worse."
            )
            response_parts.append(
                "\n\n**Try this:** Write down what your inner critic is saying. "
                "Then, write what a compassionate friend would say to you instead. "
                "Which voice is more likely to help you grow and heal?"
            )
            response_parts.append(f"\n\n{random.choice(self.socratic_questions)}")

        else:
            # General CBT response
            response_parts.append(
                "\n\nIn CBT, we work on the connection between thoughts, feelings, and behaviors. "
                "Often, changing how we think about a situation can change how we feel and act."
            )
            response_parts.append(f"\n\n{random.choice(self.socratic_questions)}")

        # 3. Engagement question
        response_parts.append(
            "\n\nWhat comes up for you when you consider these questions?"
        )

        # Combine all parts
        response = "".join(response_parts)

        logger.info(f"CBT Expert generated response (length: {len(response)} chars)")
        return response

    def get_psychoeducation(self, topic: str) -> Optional[str]:
        """
        Provide psychoeducation about CBT concepts

        Args:
            topic: Topic to explain (e.g., "anxiety", "cognitive_distortions")

        Returns:
            str: Educational content about the topic
        """

        psychoed = {
            "anxiety": (
                "**Understanding Anxiety:**\n\n"
                "Anxiety is your body's alarm system. It evolved to protect us from danger. "
                "The problem is, our alarm system can't tell the difference between a real threat "
                "(a tiger) and a perceived threat (a presentation).\n\n"
                "When anxious, you might notice:\n"
                "- Racing heart, rapid breathing\n"
                "- Muscle tension\n"
                "- Worried thoughts\n"
                "- Urge to avoid\n\n"
                "CBT helps by:\n"
                "1. Identifying anxious thoughts\n"
                "2. Testing their accuracy\n"
                "3. Responding to anxiety in new ways\n"
                "4. Gradually facing feared situations"
            ),

            "depression": (
                "**Understanding Depression:**\n\n"
                "Depression involves changes in:\n"
                "- **Mood:** Sadness, numbness, irritability\n"
                "- **Thinking:** Negative thoughts, hopelessness, difficulty concentrating\n"
                "- **Behavior:** Withdrawal, low energy, sleep changes\n"
                "- **Physical:** Fatigue, appetite changes\n\n"
                "The CBT Model of Depression:\n"
                "Depression creates a cycle:\n"
                "Feel bad ' Think negatively ' Do less ' Feel worse\n\n"
                "We break this cycle by:\n"
                "1. **Behavioral Activation:** Doing things even when you don't feel like it\n"
                "2. **Thought Challenging:** Examining negative thoughts\n"
                "3. **Problem-Solving:** Addressing practical problems\n"
                "4. **Self-Compassion:** Treating yourself with kindness"
            ),

            "cognitive_distortions": (
                "**Common Cognitive Distortions:**\n\n"
                "Our minds don't always think accurately. Here are common thinking errors:\n\n"
                "1. **All-or-Nothing:** Seeing things as perfect or terrible, no middle ground\n"
                "2. **Catastrophizing:** Jumping to worst-case scenarios\n"
                "3. **Overgeneralization:** One event means everything will go wrong\n"
                "4. **Mind Reading:** Assuming you know what others think\n"
                "5. **Should Statements:** Rigid rules about how things 'should' be\n"
                "6. **Labeling:** Defining yourself by one characteristic\n"
                "7. **Personalization:** Blaming yourself for things outside your control\n\n"
                "Recognizing these patterns is the first step to thinking more flexibly."
            ),
        }

        return psychoed.get(topic)


# Global expert instance
cbt_expert = CBTExpert()


def get_cbt_expert() -> CBTExpert:
    """Get the global CBT expert instance"""
    return cbt_expert
