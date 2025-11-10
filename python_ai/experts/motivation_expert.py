"""
Motivation and Self-Efficacy Expert

This module implements a motivation-focused expert that helps users with:
- Procrastination and lack of motivation
- Goal-setting and achievement
- Low self-esteem and confidence
- Feeling stuck or directionless
- Imposter syndrome and self-doubt

Core Principles:
1. Motivation follows action (not the other way around)
2. Small wins build momentum
3. Self-compassion > self-criticism for growth
4. Process > outcome focus
5. Growth mindset: Abilities can be developed

Techniques Used:
- SMART goal-setting
- Behavioral activation
- Values clarification
- Self-compassion practices
- Reframing failure
- Building self-efficacy through mastery experiences

IMPORTANT: This provides motivational coaching, NOT clinical therapy.
Persistent lack of motivation may be a symptom of depression requiring professional care.
"""

import logging
import random
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MotivationExpert:
    """
    Motivation Expert for procrastination, goal-achievement, and self-efficacy

    This expert uses evidence-based motivation science and coaching techniques
    to help users overcome inertia and build confidence.
    """

    def __init__(self):
        """Initialize the Motivation expert with response templates"""

        # Opening responses that validate the struggle
        self.validations = [
            "Feeling stuck is one of the most frustrating experiences. You're not alone in this.",
            "It takes courage to admit when we're struggling with motivation. That awareness is already a step forward.",
            "The gap between where you are and where you want to be can feel enormous. Let's make it smaller together.",
            "Lack of motivation doesn't mean lack of worth. Let's explore what's getting in your way.",
        ]

        # Procrastination insights
        self.procrastination_insights = [
            (
                "**Understanding Procrastination:**\n\n"
                "Procrastination isn't laziness - it's often:\n"
                "- **Perfectionism:** 'If I can't do it perfectly, why start?'\n"
                "- **Fear of failure:** Avoiding the task avoids the risk\n"
                "- **Task overwhelm:** The project feels too big\n"
                "- **Lack of connection:** The task doesn't align with your values\n"
                "- **Decision paralysis:** Too many choices, so you choose none\n\n"
                "Which resonates most for you?"
            ),
            (
                "**The 2-Minute Rule:**\n\n"
                "Commit to working on your task for just 2 minutes. That's it.\n\n"
                "Why this works:\n"
                "1. Starting is the hardest part\n"
                "2. 2 minutes feels non-threatening\n"
                "3. Often, once you start, you'll continue\n"
                "4. Even if you stop at 2 minutes, you've made progress\n\n"
                "You don't need motivation to start. You need to start to find motivation."
            ),
            (
                "**Break It Down:**\n\n"
                "Overwhelm creates paralysis. Let's shrink the task:\n\n"
                "Take your big task and break it into the smallest possible next step.\n"
                "Not 'write the paper' ' 'open a blank document'\n"
                "Not 'get in shape' ' 'put on workout clothes'\n"
                "Not 'find a job' ' 'update one line of your resume'\n\n"
                "What's the tiniest possible next step for your task?"
            ),
        ]

        # Goal-setting frameworks
        self.goal_setting = {
            "SMART": (
                "**SMART Goal Framework:**\n\n"
                "Transform vague goals into achievable ones:\n\n"
                "- **S**pecific: What exactly will you do?\n"
                "- **M**easurable: How will you know you've succeeded?\n"
                "- **A**chievable: Is this realistic given your resources?\n"
                "- **R**elevant: Does this align with your values?\n"
                "- **T**ime-bound: When will you complete this?\n\n"
                "**Example:**\n"
                "L Vague: 'Get healthier'\n"
                " SMART: 'Walk for 15 minutes after lunch, Monday-Friday, for the next 2 weeks'\n\n"
                "What goal would you like to make SMART?"
            ),
            "Process vs Outcome": (
                "**Process Goals vs. Outcome Goals:**\n\n"
                "**Outcome goals** focus on results: 'Lose 20 pounds'\n"
                "**Process goals** focus on actions: 'Track meals and exercise 5 days/week'\n\n"
                "Why process goals work better:\n"
                "- You control the process, not the outcome\n"
                "- Builds sustainable habits\n"
                "- Provides daily wins\n"
                "- Reduces anxiety about results\n\n"
                "For every outcome you want, ask: 'What process would get me there?'"
            ),
        }

        # Self-esteem and confidence building
        self.confidence_builders = [
            (
                "**Evidence Gathering:**\n\n"
                "Low self-esteem has selective memory - it remembers failures, forgets successes.\n\n"
                "Try this:\n"
                "1. List 5 things you've accomplished (any size)\n"
                "2. List 3 challenges you've overcome\n"
                "3. List 2 skills you've developed\n\n"
                "These are facts, not opinions. Your brain may minimize them ('that doesn't count'), "
                "but that's the self-esteem talking, not reality."
            ),
            (
                "**The Comparison Trap:**\n\n"
                "You're comparing your behind-the-scenes with everyone else's highlight reel.\n\n"
                "Remember:\n"
                "- You see their success, not their struggles\n"
                "- Everyone's on a different timeline\n"
                "- Your worth isn't relative to others\n\n"
                "Instead of 'Am I good enough compared to them?'\n"
                "Ask: 'Am I better than I was yesterday?'"
            ),
            (
                "**Self-Compassion > Self-Criticism:**\n\n"
                "Research shows self-compassion is MORE motivating than self-criticism.\n\n"
                "When you fail or struggle:\n"
                "L Self-criticism: 'I'm such a failure. I'll never succeed.'\n"
                " Self-compassion: 'This is hard. Many people struggle with this. What can I learn?'\n\n"
                "Self-compassion has three elements:\n"
                "1. **Self-kindness:** Treat yourself like a good friend\n"
                "2. **Common humanity:** Everyone struggles; you're not alone\n"
                "3. **Mindfulness:** Notice your pain without exaggerating it\n\n"
                "How would you speak to a friend in your situation? Try speaking to yourself that way."
            ),
        ]

        # Imposter syndrome reframes
        self.imposter_syndrome = (
            "**Imposter Syndrome:**\n\n"
            "You feel like a fraud despite evidence of competence. You attribute success to luck, "
            "timing, or fooling others - never to your abilities.\n\n"
            "**Common thoughts:**\n"
            "- 'I just got lucky'\n"
            "- 'They'll find out I don't belong'\n"
            "- 'Anyone could do this'\n\n"
            "**Reframes:**\n"
            "1. **Normalize it:** 70% of people experience imposter syndrome\n"
            "2. **Question it:** What evidence suggests you ARE capable?\n"
            "3. **Externalize it:** This is imposter syndrome talking, not truth\n"
            "4. **Accept discomfort:** Feeling like an imposter often means you're growing\n\n"
            "The difference between you and a 'real' expert? They kept going despite feeling this way."
        )

        # Values clarification
        self.values_work = (
            "**Connecting to Your Values:**\n\n"
            "Sustainable motivation comes from alignment with what matters to you.\n\n"
            "**Common values:**\n"
            "- Connection (relationships, community)\n"
            "- Growth (learning, challenge)\n"
            "- Contribution (helping others, making a difference)\n"
            "- Creativity (self-expression, innovation)\n"
            "- Security (stability, safety)\n"
            "- Freedom (autonomy, flexibility)\n"
            "- Achievement (success, mastery)\n\n"
            "**Reflection:**\n"
            "- What values resonate most with you?\n"
            "- How does your goal connect to these values?\n"
            "- If it doesn't connect, should this even be your goal?\n\n"
            "When goals align with values, motivation becomes easier."
        )

        # Quick motivation boosts
        self.quick_boosts = [
            "**The 'Done' List:** Instead of a to-do list, write what you HAVE done today. Builds momentum and counteracts 'I never accomplish anything' thoughts.",
            "**Five-Minute Win:** Choose one tiny task you've been avoiding. Set a timer for 5 minutes and do it. The completion feeling is powerful.",
            "**Future Self Letter:** Write a letter to yourself one year from now. What do you hope to have accomplished? What advice would your future self give you today?",
            "**Momentum Ritual:** Do one small productive thing every morning (make your bed, write one sentence, do one pushup). Builds a 'I'm someone who follows through' identity.",
        ]

        # Growth mindset reminders
        self.growth_mindset = (
            "**Fixed vs. Growth Mindset:**\n\n"
            "**Fixed mindset:** 'I'm not good at this' (abilities are static)\n"
            "**Growth mindset:** 'I'm not good at this YET' (abilities can develop)\n\n"
            "Research by Carol Dweck shows:\n"
            "- Fixed mindset ' avoid challenges, give up easily, see effort as pointless\n"
            "- Growth mindset ' embrace challenges, persist through setbacks, see effort as path to mastery\n\n"
            "**Reframe your self-talk:**\n"
            "- 'I can't do this' ' 'I can't do this yet'\n"
            "- 'I'm bad at this' ' 'I'm learning this'\n"
            "- 'This is too hard' ' 'This will take time and effort'\n"
            "- 'I failed' ' 'I learned what doesn't work'\n\n"
            "Your abilities are not fixed. Struggle is part of growth, not evidence you lack talent."
        )

        logger.info("Motivation Expert initialized")

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict],
        context: Optional[Dict] = None
    ) -> str:
        """
        Generate a motivation-focused response

        Args:
            user_message: The user's current message
            conversation_history: Recent conversation for context
            context: Additional context (routing scores, user metadata, etc.)

        Returns:
            str: The motivation expert's response
        """

        message_lower = user_message.lower()

        # Detect primary concern
        is_procrastinating = any(word in message_lower for word in [
            'procrastinating', 'procrastination', 'putting off', 'avoiding', 'can\'t start'
        ])

        is_unmotivated = any(word in message_lower for word in [
            'no motivation', 'unmotivated', 'don\'t feel like', 'no energy', 'no drive'
        ])

        is_stuck = any(word in message_lower for word in [
            'stuck', 'going nowhere', 'stagnant', 'not progressing', 'plateau'
        ])

        is_low_confidence = any(word in message_lower for word in [
            'not good enough', 'low self-esteem', 'no confidence', 'feel worthless', 'imposter'
        ])

        is_goal_related = any(word in message_lower for word in [
            'goal', 'achieve', 'accomplish', 'success', 'reach', 'attain'
        ])

        is_failure = any(word in message_lower for word in [
            'failed', 'failure', 'gave up', 'quit', 'didn\'t work'
        ])

        # Build response
        response_parts = []

        # 1. Validation
        response_parts.append(random.choice(self.validations))

        # 2. Concern-specific intervention
        if is_procrastinating:
            response_parts.append("\n\n" + random.choice(self.procrastination_insights))

        elif is_unmotivated or is_stuck:
            response_parts.append(
                "\n\nA lack of motivation often isn't the real problem - it's a symptom. "
                "Let's look deeper."
            )
            response_parts.append(f"\n\n{self.values_work}")
            response_parts.append(
                "\n\n**Remember:** Motivation is unreliable. Discipline and systems matter more. "
                "Build a system that works even when you don't feel motivated."
            )

        elif 'imposter' in message_lower:
            response_parts.append(f"\n\n{self.imposter_syndrome}")

        elif is_low_confidence:
            response_parts.append("\n\n" + random.choice(self.confidence_builders))
            response_parts.append(f"\n\n{self.growth_mindset}")

        elif is_goal_related:
            response_parts.append(
                "\n\nGoal-setting is powerful, but how we set goals determines whether we achieve them."
            )
            response_parts.append(f"\n\n{self.goal_setting['SMART']}")
            response_parts.append(f"\n\n{self.goal_setting['Process vs Outcome']}")

        elif is_failure:
            response_parts.append(
                "\n\nFailure is feedback, not a verdict on your worth.\n\n"
                "Every successful person has failed repeatedly. The difference? They kept going.\n\n"
                "**Questions for growth:**\n"
                "1. What did this teach you?\n"
                "2. What would you do differently next time?\n"
                "3. What did you do well, even if the outcome wasn't what you wanted?\n"
                "4. Is this a reason to quit, or to adjust your approach?\n\n"
                "Thomas Edison tested 10,000 materials for the light bulb filament. "
                "He didn't fail 10,000 times - he found 10,000 things that didn't work."
            )
            response_parts.append(f"\n\n{self.growth_mindset}")

        else:
            # General motivation response
            response_parts.append(
                "\n\nMotivation is often backwards from what we think:\n\n"
                "We think: **Motivation ' Action ' Results**\n"
                "Reality: **Action ' Results ' Motivation**\n\n"
                "Start tiny. Build momentum. Motivation will follow."
            )
            response_parts.append(f"\n\n{random.choice(self.quick_boosts)}")

        # 3. Action-oriented closing
        response_parts.append(
            "\n\nWhat's one small action you could take in the next 24 hours? "
            "Not what you 'should' do - what actually feels doable right now?"
        )

        # Combine all parts
        response = "".join(response_parts)

        logger.info(f"Motivation Expert generated response (length: {len(response)} chars)")
        return response

    def get_quick_win_suggestion(self) -> str:
        """Return a random quick motivation boost"""
        return random.choice(self.quick_boosts)


# Global expert instance
motivation_expert = MotivationExpert()


def get_motivation_expert() -> MotivationExpert:
    """Get the global motivation expert instance"""
    return motivation_expert
