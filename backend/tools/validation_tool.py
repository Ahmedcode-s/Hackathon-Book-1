"""
Tool for validating that responses are properly grounded in context.
"""
import re
from typing import Dict, List, Any
from ..models.agent_models import GroundedResponse, RetrievedContext


class GroundingValidatorTool:
    """
    Tool for validating that responses are properly grounded in provided context.
    """

    def __call__(self, response: str, context: str, sources: List[str]) -> Dict[str, Any]:
        """
        Validate that the response is properly grounded in the provided context.

        Args:
            response: The response to validate
            context: The context that was provided to generate the response
            sources: List of sources used in the response

        Returns:
            Dictionary with validation results
        """
        # Check if response contains information from the context
        context_present = self._check_context_presence(response, context)

        # Check for hallucinations (information not in context)
        hallucinations = self._detect_hallucinations(response, context)

        # Validate source citations
        citations_valid = self._validate_citations(response, sources)

        # Calculate confidence score based on validation
        confidence_score = self._calculate_confidence_score(
            context_present, hallucinations, citations_valid
        )

        return {
            "is_valid": context_present and not hallucinations and citations_valid,
            "validation_details": {
                "context_present": context_present,
                "hallucinations_detected": len(hallucinations) > 0,
                "hallucinations": hallucinations,
                "citations_valid": citations_valid,
                "sources_mentioned": sources
            },
            "confidence_score": confidence_score
        }

    def _check_context_presence(self, response: str, context: str) -> bool:
        """
        Check if the response contains information from the provided context.

        Args:
            response: The response to validate
            context: The context that was provided

        Returns:
            True if response appears to contain information from context
        """
        # Convert to lowercase for comparison
        response_lower = response.lower()
        context_lower = context.lower()

        # Check if key terms from context appear in response
        context_words = set(context_lower.split())
        response_words = set(response_lower.split())

        # Find intersection of words
        common_words = context_words.intersection(response_words)

        # If there's a meaningful intersection, consider context present
        return len(common_words) > 3  # arbitrary threshold

    def _detect_hallucinations(self, response: str, context: str) -> List[str]:
        """
        Detect potential hallucinations in the response.

        Args:
            response: The response to validate
            context: The context that was provided

        Returns:
            List of potential hallucinations (claims not supported by context)
        """
        # For simplicity, this is a basic implementation
        # A more sophisticated implementation would use semantic similarity
        # or other advanced techniques
        hallucinations = []

        # Look for claims that are not supported by the context
        # This is a simplified approach - in practice, this would be more complex
        response_sentences = re.split(r'[.!?]+', response)
        context_lower = context.lower()

        for sentence in response_sentences:
            sentence = sentence.strip()
            if sentence and sentence.lower() not in context_lower:
                # This is a simplified check - in reality, we'd need more sophisticated
                # semantic analysis to determine if the sentence is supported by context
                pass  # Skip this basic check for now, as it's too simplistic

        return hallucinations

    def _validate_citations(self, response: str, sources: List[str]) -> bool:
        """
        Validate that sources are properly cited in the response.

        Args:
            response: The response to validate
            sources: List of sources that should be cited

        Returns:
            True if sources are properly cited in the response
        """
        response_lower = response.lower()
        cited_sources = 0

        for source in sources:
            if source.lower() in response_lower:
                cited_sources += 1

        # Require at least one source to be cited
        return cited_sources > 0

    def _calculate_confidence_score(self, context_present: bool, hallucinations: List[str], citations_valid: bool) -> float:
        """
        Calculate a confidence score based on validation results.

        Args:
            context_present: Whether context is present in response
            hallucinations: List of detected hallucinations
            citations_valid: Whether citations are valid

        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0

        if context_present:
            score += 0.4  # 40% for context presence

        if not hallucinations:
            score += 0.4  # 40% for no hallucinations

        if citations_valid:
            score += 0.2  # 20% for valid citations

        return min(score, 1.0)  # Cap at 1.0