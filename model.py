import re
from collections import Counter

class CareerRecommendationModel:
    def __init__(self):
        self.interest_keywords = self._build_interest_keywords()
    
    def _build_interest_keywords(self):
        """Build a mapping of interests to related keywords"""
        return {
            'Technology': ['technology', 'tech', 'software', 'computer', 'digital', 'programming', 'coding'],
            'Programming': ['programming', 'coding', 'software', 'developer', 'code', 'algorithm'],
            'Mathematics': ['math', 'mathematics', 'calculation', 'analytical', 'numbers', 'statistics'],
            'Science': ['science', 'scientific', 'research', 'experiment', 'analysis'],
            'Engineering': ['engineering', 'engineer', 'design', 'technical', 'mechanical', 'electrical'],
            'Art': ['art', 'artistic', 'creative', 'design', 'visual', 'aesthetic'],
            'Design': ['design', 'designer', 'creative', 'visual', 'graphic', 'layout'],
            'Creativity': ['creative', 'creativity', 'innovation', 'imagination', 'artistic'],
            'Writing': ['writing', 'writer', 'content', 'blog', 'article', 'language'],
            'Communication': ['communication', 'communicate', 'social', 'interpersonal', 'presentation'],
            'Business': ['business', 'commercial', 'enterprise', 'management', 'strategy'],
            'Finance': ['finance', 'financial', 'money', 'investment', 'economics', 'banking'],
            'Marketing': ['marketing', 'advertising', 'promotion', 'brand', 'campaign'],
            'Analytics': ['analytics', 'analysis', 'data', 'statistics', 'metrics', 'insights'],
            'Strategy': ['strategy', 'strategic', 'planning', 'business', 'management'],
            'Psychology': ['psychology', 'psychological', 'mental', 'behavior', 'human'],
            'Human Behavior': ['behavior', 'human', 'psychology', 'social', 'people'],
            'Research': ['research', 'study', 'investigation', 'analysis', 'scientific'],
            'Medicine': ['medicine', 'medical', 'health', 'healthcare', 'clinical', 'patient'],
            'Biology': ['biology', 'biological', 'life', 'organism', 'genetics', 'biomedical'],
            'Environment': ['environment', 'environmental', 'nature', 'sustainability', 'green'],
            'Sustainability': ['sustainability', 'sustainable', 'environment', 'green', 'eco'],
            'Nature': ['nature', 'natural', 'environment', 'outdoor', 'wildlife'],
            'Problem Solving': ['problem', 'solve', 'solution', 'analytical', 'critical', 'thinking'],
            'Innovation': ['innovation', 'innovative', 'creative', 'technology', 'new'],
            'Statistics': ['statistics', 'statistical', 'data', 'analysis', 'mathematics'],
            'Visual Arts': ['visual', 'art', 'graphic', 'design', 'aesthetic', 'creative'],
            'Aesthetics': ['aesthetic', 'beauty', 'design', 'visual', 'art'],
            'Social Media': ['social', 'media', 'digital', 'marketing', 'communication', 'online'],
            'Economics': ['economics', 'economic', 'finance', 'market', 'business'],
            'Physics': ['physics', 'physical', 'mechanical', 'engineering', 'science'],
            'Empathy': ['empathy', 'empathic', 'human', 'psychology', 'caring', 'helping'],
            'Language': ['language', 'linguistic', 'communication', 'writing', 'translation']
        }
    
    def _calculate_interest_match(self, user_interests, career_interests_str):
        """Calculate how well user interests match career requirements"""
        if not career_interests_str:
            return 0
        
        career_interests = [i.strip() for i in career_interests_str.split(',')]
        user_interests_lower = [i.lower() for i in user_interests]
        career_interests_lower = [i.lower() for i in career_interests]
        
        # Direct matches
        direct_matches = sum(1 for interest in user_interests_lower 
                           if interest in career_interests_lower)
        
        # Keyword-based matches
        keyword_matches = 0
        for user_interest in user_interests:
            user_interest_lower = user_interest.lower()
            if user_interest_lower in self.interest_keywords:
                keywords = self.interest_keywords[user_interest_lower]
                for career_interest in career_interests:
                    career_interest_lower = career_interest.lower()
                    if any(keyword in career_interest_lower for keyword in keywords):
                        keyword_matches += 0.5
                        break
        
        # Calculate match score (0-100)
        total_possible = len(career_interests)
        if total_possible == 0:
            return 0
        
        match_score = min(100, ((direct_matches + keyword_matches) / total_possible) * 100)
        return round(match_score, 1)
    
    def _generate_explanation(self, user_interests, career_interests_str, career_name, match_score):
        """Generate an explanation for why a career was recommended"""
        career_interests = [i.strip() for i in career_interests_str.split(',')]
        user_interests_lower = [i.lower() for i in user_interests]
        career_interests_lower = [i.lower() for i in career_interests]
        
        # Find matching interests
        matching_interests = []
        for interest in user_interests:
            if interest.lower() in career_interests_lower:
                matching_interests.append(interest)
        
        # Find related interests
        related_interests = []
        for user_interest in user_interests:
            user_interest_lower = user_interest.lower()
            if user_interest_lower in self.interest_keywords:
                keywords = self.interest_keywords[user_interest_lower]
                for career_interest in career_interests:
                    if any(keyword in career_interest.lower() for keyword in keywords):
                        if user_interest not in matching_interests:
                            related_interests.append(user_interest)
                            break
        
        # Build explanation
        explanation_parts = []
        
        if matching_interests:
            if len(matching_interests) == 1:
                explanation_parts.append(
                    f"Your interest in {matching_interests[0]} directly aligns with this career path."
                )
            else:
                interests_str = ', '.join(matching_interests[:-1]) + f", and {matching_interests[-1]}"
                explanation_parts.append(
                    f"Your interests in {interests_str} directly match the requirements for {career_name}."
                )
        
        if related_interests:
            if len(related_interests) == 1:
                explanation_parts.append(
                    f"Your interest in {related_interests[0]} is also relevant to this field."
                )
            else:
                interests_str = ', '.join(related_interests[:-1]) + f", and {related_interests[-1]}"
                explanation_parts.append(
                    f"Additionally, your interests in {interests_str} complement this career."
                )
        
        if match_score >= 70:
            explanation_parts.append(
                f"With a {match_score}% match score, {career_name} is an excellent fit for your profile."
            )
        elif match_score >= 50:
            explanation_parts.append(
                f"With a {match_score}% match score, {career_name} shows strong potential for your interests."
            )
        else:
            explanation_parts.append(
                f"While there's a {match_score}% match, {career_name} may still be worth exploring based on your interests."
            )
        
        return ' '.join(explanation_parts)
    
    def get_recommendations(self, user_interests, careers_data):
        """
        Get career recommendations based on user interests
        
        Args:
            user_interests: List of user's interests
            careers_data: List of tuples (name, description, required_interests, skills)
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        for career in careers_data:
            name, description, required_interests, skills = career
            
            # Calculate match score
            match_score = self._calculate_interest_match(user_interests, required_interests)
            
            # Generate explanation
            explanation = self._generate_explanation(
                user_interests, required_interests, name, match_score
            )
            
            recommendations.append({
                'career': name,
                'description': description,
                'match_score': match_score,
                'explanation': explanation
            })
        
        # Sort by match score (descending)
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top 5 recommendations
        return recommendations[:5]