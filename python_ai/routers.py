"""
Mixture of Experts (MoE) Router

This module implements semantic routing to direct user messages to the appropriate
therapy expert (CBT, Mindfulness, or Motivation).

How it works:
1. Each expert has a description of what issues it handles
2. User message is embedded into a vector space
3. Expert descriptions are embedded into the same vector space
4. Cosine similarity determines which expert is the best match
5. Message is routed to that expert for response generation

This is a "soft" MoE approach:
- Routing is based on semantic similarity, not hard rules
- Can be extended to multi-expert responses (e.g., CBT + mindfulness)
- Learns from data if we collect user feedback on routing quality

Alternative approaches we're NOT using (and why):
- Keyword matching: Too brittle, misses synonyms
- Classification model: Requires labeled training data
- LLM-based routing: Adds latency and cost
- User selection: Burdens user with technical knowledge
"""

import logging
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
import numpy as np

from memory.embeddings import embedder, find_most_similar

logger = logging.getLogger(__name__)


# ==================== Expert Descriptions ====================

@dataclass
class ExpertProfile:
    """
    Profile for each therapy expert

    Contains:
    - name: Expert identifier (cbt, mindfulness, motivation)
    - display_name: User-friendly name
    - description: Semantic description of what this expert handles
    - example_queries: Sample user messages this expert should handle
    """
    name: str
    display_name: str
    description: str
    example_queries: List[str]


# Define each expert's specialty
# These descriptions are carefully crafted to:
# 1. Use vocabulary that matches user language
# 2. Cover the semantic space of relevant concerns
# 3. Avoid overlap between experts (for clear routing)

CBT_EXPERT = ExpertProfile(
    name="cbt",
    display_name="CBT Therapist",
    description=(
        "Cognitive Behavioral Therapy expert specializing in anxiety, worry, depression, "
        "negative thoughts, catastrophic thinking, rumination, panic attacks, social anxiety, "
        "fear, phobias, obsessive thoughts, irrational beliefs, cognitive distortions, "
        "thought patterns, mental spirals, overthinking, self-criticism, and emotional regulation."
    ),
    example_queries=[
        "I can't stop worrying about everything",
        "I keep having negative thoughts",
        "I'm so anxious all the time",
        "I feel depressed and hopeless",
        "I keep overthinking everything",
        "My mind won't stop racing",
        "I'm afraid of social situations",
    ]
)

MINDFULNESS_EXPERT = ExpertProfile(
    name="mindfulness",
    display_name="Mindfulness Coach",
    description=(
        "Mindfulness and meditation expert specializing in stress, overwhelm, burnout, "
        "being present, grounding, breathing exercises, relaxation, tension, restlessness, "
        "sleep problems, insomnia, racing mind, difficulty focusing, distraction, "
        "needing calm, wanting peace, feeling scattered, needing to slow down, "
        "body awareness, and mind-body connection."
    ),
    example_queries=[
        "I'm so stressed out",
        "I feel overwhelmed",
        "I can't relax",
        "I need to calm down",
        "I can't sleep",
        "I'm feeling scattered",
        "I need help focusing",
        "I want to feel more peaceful",
    ]
)

MOTIVATION_EXPERT = ExpertProfile(
    name="motivation",
    display_name="Motivation Coach",
    description=(
        "Motivation and self-efficacy expert specializing in procrastination, lack of motivation, "
        "low energy, feeling stuck, goal-setting, achievement, productivity, self-discipline, "
        "confidence, self-esteem, self-worth, imposter syndrome, failure, giving up, "
        "losing hope in goals, career stress, performance anxiety, feeling unmotivated, "
        "lack of direction, purpose, and personal growth."
    ),
    example_queries=[
        "I have no motivation",
        "I keep procrastinating",
        "I feel stuck in life",
        "I can't seem to achieve my goals",
        "I have low self-esteem",
        "I feel like I'm not good enough",
        "I keep giving up on things",
        "I lack confidence",
    ]
)


# All experts in one structure
ALL_EXPERTS = [CBT_EXPERT, MINDFULNESS_EXPERT, MOTIVATION_EXPERT]


# ==================== Router Class ====================

class SemanticRouter:
    """
    Semantic Router using embedding-based similarity

    This router determines which expert should handle a user's message
    by comparing the semantic similarity between the message and each
    expert's description.

    Process:
    1. Encode expert descriptions once at initialization (cached)
    2. For each user message:
        a. Encode the message
        b. Calculate similarity to each expert
        c. Route to the expert with highest similarity
        d. Apply confidence threshold to avoid bad routing

    Attributes:
        expert_embeddings: Dict mapping expert names to their embedding vectors
        confidence_threshold: Minimum similarity score to route (default 0.3)
    """

    def __init__(self, confidence_threshold: float = 0.3):
        """
        Initialize the semantic router

        Args:
            confidence_threshold: Minimum similarity score required for routing
                                 If no expert meets this threshold, route to default (CBT)
                                 Range: 0.0 to 1.0
                                 Typical values:
                                 - 0.2: Very permissive (accept weak matches)
                                 - 0.3: Balanced (default)
                                 - 0.5: Conservative (only strong matches)
        """
        self.confidence_threshold = confidence_threshold
        self.expert_embeddings: Dict[str, np.ndarray] = {}
        self.default_expert = "cbt"  # Fallback if no good match

        # Pre-compute expert embeddings
        self._initialize_expert_embeddings()

        logger.info(f"SemanticRouter initialized with {len(self.expert_embeddings)} experts")
        logger.info(f"Confidence threshold: {self.confidence_threshold}")

    def _initialize_expert_embeddings(self):
        """
        Pre-compute embeddings for all expert descriptions

        This is done once at startup to avoid re-computing on every message.
        The embeddings are cached in memory for fast routing.
        """
        logger.info("Computing expert embeddings...")

        for expert in ALL_EXPERTS:
            # Encode the expert's description
            embedding = embedder.encode(expert.description)
            self.expert_embeddings[expert.name] = embedding

            logger.info(f"  {expert.display_name}: embedding shape {embedding.shape}")

        logger.info("Expert embeddings computed successfully")

    def route(self, user_message: str) -> Tuple[str, float, Dict]:
        """
        Route a user message to the appropriate expert

        This is the main routing function called for each user message.

        Algorithm:
        1. Encode user message into embedding vector
        2. Calculate cosine similarity to each expert's embedding
        3. Select expert with highest similarity
        4. If similarity < threshold, use default expert
        5. Return routing decision with metadata

        Args:
            user_message: The user's message text

        Returns:
            Tuple of (expert_name: str, confidence: float, metadata: dict)

            expert_name: Which expert should handle this message
            confidence: Similarity score (0.0 to 1.0)
            metadata: Additional routing information
                - all_scores: Dict of all expert scores
                - routing_reason: Explanation of routing decision
                - used_default: Whether we fell back to default

        Example:
            >>> router = SemanticRouter()
            >>> expert, confidence, meta = router.route("I'm feeling really anxious")
            >>> print(f"Route to {expert} with {confidence:.2f} confidence")
            Route to cbt with 0.78 confidence
        """

        # Encode the user's message
        message_embedding = embedder.encode(user_message)

        # Find most similar expert
        similarities = find_most_similar(
            message_embedding,
            self.expert_embeddings,
            top_k=len(self.expert_embeddings)
        )

        # Get the best match
        best_expert, best_score = similarities[0]

        # Prepare metadata with all scores
        all_scores = {expert: score for expert, score in similarities}

        # Check confidence threshold
        if best_score < self.confidence_threshold:
            # Low confidence - use default expert
            logger.warning(
                f"Low routing confidence ({best_score:.3f} < {self.confidence_threshold}). "
                f"Using default expert: {self.default_expert}"
            )

            metadata = {
                "all_scores": all_scores,
                "routing_reason": f"Low confidence ({best_score:.3f}), using default",
                "used_default": True,
                "original_best_match": best_expert,
            }

            return self.default_expert, best_score, metadata

        else:
            # Confident routing
            logger.info(
                f"Routing to {best_expert} with confidence {best_score:.3f}. "
                f"Scores: {', '.join([f'{e}={s:.3f}' for e, s in similarities])}"
            )

            metadata = {
                "all_scores": all_scores,
                "routing_reason": f"Best semantic match ({best_score:.3f})",
                "used_default": False,
            }

            return best_expert, best_score, metadata

    def get_expert_profile(self, expert_name: str) -> Optional[ExpertProfile]:
        """
        Get the profile for a specific expert

        Args:
            expert_name: Name of the expert (cbt, mindfulness, motivation)

        Returns:
            ExpertProfile if found, None otherwise
        """
        for expert in ALL_EXPERTS:
            if expert.name == expert_name:
                return expert
        return None

    def test_routing(self):
        """
        Test the router with example queries

        This is useful for:
        - Debugging routing behavior
        - Validating that experts are properly differentiated
        - Tuning the confidence threshold

        Prints routing results for all example queries.
        """
        logger.info("\n" + "="*60)
        logger.info("ROUTING TEST - Example Queries")
        logger.info("="*60 + "\n")

        for expert in ALL_EXPERTS:
            logger.info(f"\n--- Testing {expert.display_name} ---")
            for query in expert.example_queries:
                routed_expert, confidence, metadata = self.route(query)
                is_correct = routed_expert == expert.name

                status = "" if is_correct else ""
                logger.info(
                    f"{status} '{query}' � {routed_expert} "
                    f"(confidence: {confidence:.3f})"
                )

        logger.info("\n" + "="*60 + "\n")


# ==================== Global Router Instance ====================

# Create a global router instance
# This is initialized once and reused across all requests
router = SemanticRouter(confidence_threshold=0.3)


def get_router() -> SemanticRouter:
    """
    Get the global router instance

    Used for dependency injection in FastAPI endpoints
    """
    return router
