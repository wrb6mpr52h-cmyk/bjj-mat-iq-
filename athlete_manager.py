"""
BJJ Mat IQ - Athlete Management System
Handles athlete profiles, match history tracking, and cross-match progress analysis
with user-based data isolation and role-based access control.
"""

import json
import os
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import statistics

class AthleteManager:
    """Manages athlete profiles and cross-match progress tracking with user isolation."""
    
    def __init__(self, base_dir="data", current_user=None, user_role="individual"):
        self.base_dir = base_dir
        self.current_user = current_user
        self.user_role = user_role  # "admin", "team_owner", "individual"
        
        # Create directory structure
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(os.path.join(base_dir, "athletes"), exist_ok=True)
        os.makedirs(os.path.join(base_dir, "reviews"), exist_ok=True)
        
        # User-specific directories
        if current_user:
            user_dir = os.path.join(base_dir, "users", current_user)
            os.makedirs(os.path.join(user_dir, "athletes"), exist_ok=True)
            os.makedirs(os.path.join(user_dir, "reviews"), exist_ok=True)
    
    def _get_athlete_dirs(self) -> List[str]:
        """Get list of directories to search based on user role."""
        dirs = []
        
        if self.user_role == "admin":
            # Admin sees all athletes
            global_dir = os.path.join(self.base_dir, "athletes")
            if os.path.exists(global_dir):
                dirs.append(global_dir)
            
            # Also include all user directories
            users_dir = os.path.join(self.base_dir, "users")
            if os.path.exists(users_dir):
                for user_folder in os.listdir(users_dir):
                    user_athlete_dir = os.path.join(users_dir, user_folder, "athletes")
                    if os.path.exists(user_athlete_dir):
                        dirs.append(user_athlete_dir)
        
        elif self.user_role == "team_owner":
            # Team owners see their own athletes and their team's athletes
            if self.current_user:
                user_dir = os.path.join(self.base_dir, "users", self.current_user, "athletes")
                if os.path.exists(user_dir):
                    dirs.append(user_dir)
        
        elif self.user_role == "individual":
            # Individual users only see their own athletes
            if self.current_user:
                user_dir = os.path.join(self.base_dir, "users", self.current_user, "athletes")
                if os.path.exists(user_dir):
                    dirs.append(user_dir)
                
                # Also check global athletes directory for owned athletes
                global_dir = os.path.join(self.base_dir, "athletes")
                if os.path.exists(global_dir):
                    dirs.append(global_dir)
                
                # Check root directory for scattered files (fallback for deployment issues)
                if os.path.exists("."):
                    dirs.append(".")
        
        return dirs
    
    def _get_review_dirs(self) -> List[str]:
        """Get list of review directories to search based on user role."""
        dirs = []
        
        if self.user_role == "admin":
            # Admin sees all reviews
            global_dir = os.path.join(self.base_dir, "reviews")
            if os.path.exists(global_dir):
                dirs.append(global_dir)
            
            # Also include all user directories
            users_dir = os.path.join(self.base_dir, "users")
            if os.path.exists(users_dir):
                for user_folder in os.listdir(users_dir):
                    user_review_dir = os.path.join(users_dir, user_folder, "reviews")
                    if os.path.exists(user_review_dir):
                        dirs.append(user_review_dir)
        
        elif self.user_role == "team_owner":
            # Team owners see their own reviews and their team's reviews
            if self.current_user:
                user_dir = os.path.join(self.base_dir, "users", self.current_user, "reviews")
                if os.path.exists(user_dir):
                    dirs.append(user_dir)
                
                # Also check global directory for backward compatibility
                global_dir = os.path.join(self.base_dir, "reviews")
                if os.path.exists(global_dir):
                    dirs.append(global_dir)
        
        elif self.user_role == "individual":
            # Individual users see their own reviews
            if self.current_user:
                user_dir = os.path.join(self.base_dir, "users", self.current_user, "reviews")
                if os.path.exists(user_dir):
                    dirs.append(user_dir)
                
                # Also check global directory for backward compatibility (filter by owner)
                global_dir = os.path.join(self.base_dir, "reviews")
                if os.path.exists(global_dir):
                    dirs.append(global_dir)
        
        return dirs
    
    def _get_user_athlete_dir(self) -> str:
        """Get the athlete directory for the current user."""
        if not self.current_user:
            return os.path.join(self.base_dir, "athletes")
        return os.path.join(self.base_dir, "users", self.current_user, "athletes")
    
    def _get_user_review_dir(self) -> str:
        """Get the review directory for the current user."""
        if not self.current_user:
            return os.path.join(self.base_dir, "reviews")
        return os.path.join(self.base_dir, "users", self.current_user, "reviews")
    
    def _can_access_athlete(self, athlete_profile: Dict) -> bool:
        """Check if current user can access this athlete."""
        if self.user_role == "admin":
            return True
        
        athlete_owner = athlete_profile.get("owner")
        athlete_team = athlete_profile.get("team", "")
        athlete_id = athlete_profile.get("athlete_id")
        
        if self.user_role == "team_owner":
            # Team owners can see their own athletes and their team's athletes
            if athlete_owner == self.current_user:
                return True
            # Add logic here to check if athlete belongs to team owner's team
            # For now, just check if user has team ownership permissions for this team
            return False
        
        elif self.user_role == "individual":
            # Individual users only see their own athletes
            if athlete_owner == self.current_user:
                return True
            
            # Also check owned_athletes field in users.json file
            if athlete_id and self.current_user:
                try:
                    from user_manager import UserManager
                    user_manager = UserManager()
                    user_info = user_manager.get_user_info(self.current_user)
                    if user_info and athlete_id in user_info.get("owned_athletes", []):
                        return True
                except:
                    pass  # Fallback to owner field check only
            
            return False
        
        return False
    
    def create_athlete_id(self, name: str, team: str = "") -> str:
        """Generate a unique athlete ID from name and team."""
        base_name = name.lower().replace(" ", "_").replace("'", "").replace(".", "")
        if team:
            team_part = team.lower().replace(" ", "_").replace("'", "").replace(".", "")[:10]
            return f"{base_name}_{team_part}"
        return base_name
    
    def get_athlete_profile(self, athlete_id: str) -> Optional[Dict]:
        """Load athlete profile from file, respecting user permissions."""
        # Search in all accessible directories
        for athlete_dir in self._get_athlete_dirs():
            profile_path = os.path.join(athlete_dir, f"{athlete_id}.json")
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    profile = json.load(f)
                
                # Check access permissions
                if self._can_access_athlete(profile):
                    return profile
        
        return None
    
    def create_or_update_athlete(self, name: str, team: str = "", belt: str = "", 
                                age_division: str = "", weight_class: str = "", notes: str = "") -> str:
        """Create or update athlete profile in user's directory."""
        athlete_id = self.create_athlete_id(name, team)
        
        # Use user-specific directory
        athlete_dir = self._get_user_athlete_dir()
        profile_path = os.path.join(athlete_dir, f"{athlete_id}.json")
        
        # Load existing profile or create new
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = json.load(f)
        else:
            profile = {
                "athlete_id": athlete_id,
                "name": name,
                "team": team,
                "owner": self.current_user,  # Track ownership
                "created_at": datetime.now().isoformat(),
                "match_history": [],
                "belt_progression": [],
                "notes": ""
            }
        
        # Update profile data
        profile["name"] = name
        profile["team"] = team
        if belt:
            profile["current_belt"] = belt
            # Track belt progression
            if not profile.get("belt_progression") or profile["belt_progression"][-1]["belt"] != belt:
                profile.setdefault("belt_progression", []).append({
                    "belt": belt,
                    "date": datetime.now().isoformat()[:10]
                })
        if age_division:
            profile["current_age_division"] = age_division
        if weight_class:
            profile["current_weight_class"] = weight_class
        if notes:
            profile["notes"] = notes
        
        profile["last_updated"] = datetime.now().isoformat()
        
        # Save profile
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2)
        
        return athlete_id
    
    def link_match_to_athlete(self, athlete_id: str, review_id: str):
        """Link a match review to an athlete's history."""
        profile = self.get_athlete_profile(athlete_id)
        if not profile:
            return False
        
        if review_id not in profile.get("match_history", []):
            profile.setdefault("match_history", []).append(review_id)
            
        # Find the correct directory for this athlete
        athlete_dir = self._get_user_athlete_dir()
        profile_path = os.path.join(athlete_dir, f"{athlete_id}.json")
        
        # If not found in user dir, check if we have access to it elsewhere
        if not os.path.exists(profile_path):
            for search_dir in self._get_athlete_dirs():
                test_path = os.path.join(search_dir, f"{athlete_id}.json")
                if os.path.exists(test_path):
                    profile_path = test_path
                    break
        
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2)
        
        return True
    
    def get_athlete_matches(self, athlete_id: str) -> List[Dict]:
        """Get all matches for an athlete from accessible review directories."""
        profile = self.get_athlete_profile(athlete_id)
        if not profile:
            return []
        
        matches = []
        for review_id in profile.get("match_history", []):
            # Search across accessible review directories
            for review_dir in self._get_review_dirs():
                review_path = os.path.join(review_dir, f"{review_id}.json")
                if os.path.exists(review_path):
                    with open(review_path, 'r') as f:
                        match_data = json.load(f)
                        matches.append(match_data)
                    break  # Found the review, no need to check other directories
        
        # Sort by date
        matches.sort(key=lambda x: x.get("metadata", {}).get("reviewed_at", ""))
        return matches
    
    def get_progress_analysis(self, athlete_id: str) -> Dict:
        """Analyze athlete's progress across all matches and assessments."""
        matches = self.get_athlete_matches(athlete_id)
        
        # Get assessments
        athlete_profile = self.get_athlete_profile(athlete_id)
        assessment_reports = athlete_profile.get("assessment_reports", []) if athlete_profile else []
        
        # Load actual assessment data
        skill_assessments = []
        for assessment_info in assessment_reports:
            file_path = assessment_info.get("file_path", "")
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        assessment_data = json.load(f)
                        skill_assessments.append(assessment_data)
                except (json.JSONDecodeError, IOError):
                    continue
        
        total_reviews = len(matches) + len(skill_assessments)
        
        if total_reviews < 2:
            return {"error": f"Need at least 2 reviews for progress analysis (found {total_reviews})"}

        analysis = {
            "total_matches": len(matches),
            "total_assessments": len(skill_assessments),
            "total_reviews": total_reviews,
            "date_range": self._calculate_date_range(matches, skill_assessments),
            "win_loss_record": self._calculate_win_loss_record(matches),
            "assessment_trends": self._calculate_combined_assessment_trends(matches, skill_assessments),
            "improvement_areas": self._identify_improvement_areas_combined(matches, skill_assessments),
            "consistency_analysis": self._analyze_consistency_combined(matches, skill_assessments),
            "recent_performance": self._analyze_recent_performance_combined(matches, skill_assessments)
        }
        
        return analysis
    
    def _calculate_win_loss_record(self, matches: List[Dict]) -> Dict:
        """Calculate win/loss record."""
        wins = 0
        losses = 0
        draws = 0
        
        for match in matches:
            result = match.get("match_info", {}).get("result", "")
            fighter_a = match.get("match_info", {}).get("fighter_a", "")
            
            # Check if fighter_a (the athlete) wins
            if fighter_a and ("wins" in result.lower()) and (fighter_a.lower() in result.lower()):
                wins += 1
            elif "Fighter A wins" in result:  # Fallback for older format
                wins += 1
            elif "Fighter B wins" in result:  # Fighter A loses
                losses += 1
            elif result and ("loses" in result.lower() or "lost" in result.lower()) and fighter_a and (fighter_a.lower() in result.lower()):
                losses += 1
            elif result:  # Has result but not clear win/loss
                draws += 1
        
        total = wins + losses + draws
        return {
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "win_percentage": round(wins / total * 100, 1) if total > 0 else 0,
            "total_matches": total
        }
    
    def _calculate_assessment_trends(self, matches: List[Dict]) -> Dict:
        """Calculate trends in assessment scores over time."""
        trends = {}
        
        for match in matches:
            date = match.get("metadata", {}).get("reviewed_at", "")[:10]
            assessments = match.get("assessments", {})
            
            for area, data in assessments.items():
                if area not in trends:
                    trends[area] = []
                
                rating = data.get("rating", 0) if isinstance(data, dict) else data
                trends[area].append({
                    "date": date,
                    "rating": rating
                })
        
        # Calculate trend statistics
        trend_analysis = {}
        for area, scores in trends.items():
            if len(scores) >= 2:
                ratings = [s["rating"] for s in scores]
                trend_analysis[area] = {
                    "first_score": ratings[0],
                    "latest_score": ratings[-1],
                    "improvement": ratings[-1] - ratings[0],
                    "average": round(statistics.mean(ratings), 1),
                    "trend": "improving" if ratings[-1] > ratings[0] else "declining" if ratings[-1] < ratings[0] else "stable",
                    "scores": scores
                }
        
        return trend_analysis
    
    def _calculate_date_range(self, matches: List[Dict], skill_assessments: List[Dict]) -> Dict:
        """Calculate date range across all reviews."""
        all_dates = []
        
        # Add match dates
        for match in matches:
            date = match.get("metadata", {}).get("reviewed_at", "")
            if date:
                all_dates.append(date)
        
        # Add assessment dates
        for assessment in skill_assessments:
            date = assessment.get("metadata", {}).get("created_date", "")
            if date:
                all_dates.append(date)
        
        if not all_dates:
            return {"first_review": "", "latest_review": ""}
            
        all_dates.sort()
        return {
            "first_review": all_dates[0][:10],
            "latest_review": all_dates[-1][:10]
        }
    
    def _calculate_combined_assessment_trends(self, matches: List[Dict], skill_assessments: List[Dict]) -> Dict:
        """Calculate trends combining match reviews and assessments."""
        trends = {}
        
        # Process match assessments
        for match in matches:
            date = match.get("metadata", {}).get("reviewed_at", "")[:10]
            assessments = match.get("assessments", {})
            
            for area, data in assessments.items():
                if area not in trends:
                    trends[area] = []
                
                rating = data.get("rating", 0) if isinstance(data, dict) else data
                trends[area].append({
                    "date": date,
                    "rating": rating,
                    "source": "match_review"
                })
        
        # Process assessments
        for assessment in skill_assessments:
            date = assessment.get("metadata", {}).get("created_date", "")[:10]
            assessments_data = assessment.get("assessments", {})
            
            for area, data in assessments_data.items():
                if area not in trends:
                    trends[area] = []
                
                rating = data.get("rating", 0) if isinstance(data, dict) else data
                trends[area].append({
                    "date": date,
                    "rating": rating,
                    "source": "assessment"
                })
        
        # Sort by date and calculate trend statistics
        trend_analysis = {}
        for area, scores in trends.items():
            if len(scores) >= 2:
                # Sort by date
                scores.sort(key=lambda x: x["date"])
                ratings = [s["rating"] for s in scores]
                
                trend_analysis[area] = {
                    "first_score": ratings[0],
                    "latest_score": ratings[-1],
                    "improvement": ratings[-1] - ratings[0],
                    "average": round(statistics.mean(ratings), 1),
                    "trend": "improving" if ratings[-1] > ratings[0] else "declining" if ratings[-1] < ratings[0] else "stable",
                    "scores": scores,
                    "total_reviews": len(scores),
                    "match_reviews": len([s for s in scores if s["source"] == "match_review"]),
                    "assessments": len([s for s in scores if s["source"] == "assessment"])
                }
        
        return trend_analysis
    
    def _identify_improvement_areas_combined(self, matches: List[Dict], skill_assessments: List[Dict]) -> List[str]:
        """Identify areas needing improvement from all reviews."""
        all_areas = {}
        
        # Process matches
        for match in matches:
            assessments = match.get("assessments", {})
            for area, data in assessments.items():
                rating = data.get("rating", 0) if isinstance(data, dict) else data
                if area not in all_areas:
                    all_areas[area] = []
                all_areas[area].append(rating)
        
        # Process assessments
        for assessment in skill_assessments:
            assessments_data = assessment.get("assessments", {})
            for area, data in assessments_data.items():
                rating = data.get("rating", 0) if isinstance(data, dict) else data
                if area not in all_areas:
                    all_areas[area] = []
                all_areas[area].append(rating)
        
        # Find areas with consistently low scores
        improvement_areas = []
        for area, ratings in all_areas.items():
            if ratings:
                avg_rating = statistics.mean(ratings)
                latest_rating = ratings[-1]
                if avg_rating <= 2.5 or latest_rating <= 2:
                    improvement_areas.append(area)
        
        return improvement_areas
    
    def _analyze_consistency_combined(self, matches: List[Dict], skill_assessments: List[Dict]) -> Dict:
        """Analyze consistency across all reviews."""
        all_areas = {}
        
        # Collect all ratings
        for match in matches:
            assessments = match.get("assessments", {})
            for area, data in assessments.items():
                rating = data.get("rating", 0) if isinstance(data, dict) else data
                if area not in all_areas:
                    all_areas[area] = []
                all_areas[area].append(rating)
        
        for assessment in skill_assessments:
            assessments_data = assessment.get("assessments", {})
            for area, data in assessments_data.items():
                rating = data.get("rating", 0) if isinstance(data, dict) else data
                if area not in all_areas:
                    all_areas[area] = []
                all_areas[area].append(rating)
        
        consistency = {}
        for area, ratings in all_areas.items():
            if len(ratings) >= 2:
                std_dev = statistics.stdev(ratings)
                consistency[area] = {
                    "standard_deviation": round(std_dev, 2),
                    "consistency_level": "High" if std_dev < 0.5 else "Medium" if std_dev < 1.0 else "Low",
                    "total_reviews": len(ratings)
                }
        
        return consistency
    
    def _analyze_recent_performance_combined(self, matches: List[Dict], skill_assessments: List[Dict]) -> Dict:
        """Analyze recent performance trends."""
        # Combine all reviews with dates
        all_reviews = []
        
        for match in matches:
            date = match.get("metadata", {}).get("reviewed_at", "")
            all_reviews.append({
                "date": date,
                "assessments": match.get("assessments", {}),
                "type": "match"
            })
        
        for assessment in skill_assessments:
            date = assessment.get("metadata", {}).get("created_date", "")
            all_reviews.append({
                "date": date,
                "assessments": assessment.get("assessments", {}),
                "type": "assessment"
            })
        
        # Sort by date and take recent reviews
        all_reviews.sort(key=lambda x: x["date"], reverse=True)
        recent_reviews = all_reviews[:3]  # Last 3 reviews
        
        if len(recent_reviews) < 2:
            return {"insufficient_data": True}
        
        # Calculate recent performance metrics
        recent_areas = {}
        for review in recent_reviews:
            for area, data in review["assessments"].items():
                rating = data.get("rating", 0) if isinstance(data, dict) else data
                if area not in recent_areas:
                    recent_areas[area] = []
                recent_areas[area].append(rating)
        
        recent_performance = {}
        for area, ratings in recent_areas.items():
            if ratings:
                recent_performance[area] = {
                    "average": round(statistics.mean(ratings), 1),
                    "trend": "improving" if len(ratings) >= 2 and ratings[0] < ratings[-1] else "stable" if len(ratings) >= 2 and ratings[0] == ratings[-1] else "declining" if len(ratings) >= 2 else "insufficient_data",
                    "reviews_count": len(ratings)
                }
        
        return recent_performance
    
    def _identify_improvement_areas(self, matches: List[Dict]) -> Dict:
        """Identify areas that have shown improvement or need work."""
        trends = self._calculate_assessment_trends(matches)
        
        most_improved = []
        needs_work = []
        consistent_strengths = []
        
        for area, data in trends.items():
            improvement = data["improvement"]
            average = data["average"]
            latest_score = data["latest_score"]
            
            if improvement >= 1:  # Improved by 1+ point
                most_improved.append({"area": area, "improvement": improvement})
            elif improvement <= -1:  # Declined by 1+ point
                needs_work.append({"area": area, "decline": abs(improvement)})
            
            if average >= 4 and latest_score >= 4:  # Consistently strong
                consistent_strengths.append({"area": area, "average": average})
            elif average <= 2 and latest_score <= 2:  # Consistently weak
                needs_work.append({"area": area, "average": average})
        
        return {
            "most_improved": sorted(most_improved, key=lambda x: x.get("improvement", 0), reverse=True),
            "needs_work": needs_work,
            "consistent_strengths": sorted(consistent_strengths, key=lambda x: x.get("average", 0), reverse=True)
        }
    
    def _analyze_consistency(self, matches: List[Dict]) -> Dict:
        """Analyze performance consistency."""
        scores = []
        for match in matches:
            athlete_score = match.get("scores", {}).get("fighter_a", 0)
            opponent_score = match.get("scores", {}).get("fighter_b", 0)
            scores.append(athlete_score - opponent_score)  # Point differential
        
        if len(scores) < 2:
            return {"error": "Need at least 2 matches for consistency analysis"}
        
        return {
            "average_point_differential": round(statistics.mean(scores), 1),
            "consistency_score": round(1 / (statistics.stdev(scores) + 0.1), 2),  # Lower stdev = more consistent
            "most_dominant_win": max(scores),
            "worst_loss": min(scores)
        }
    
    def _analyze_recent_performance(self, matches: List[Dict], recent_count: int = 3) -> Dict:
        """Analyze recent performance trends."""
        if len(matches) < recent_count:
            recent_matches = matches
        else:
            recent_matches = matches[-recent_count:]
        
        # Compare recent vs overall performance
        overall_win_rate = self._calculate_win_loss_record(matches)["win_percentage"]
        recent_win_rate = self._calculate_win_loss_record(recent_matches)["win_percentage"]
        
        return {
            "recent_matches_count": len(recent_matches),
            "recent_win_rate": recent_win_rate,
            "overall_win_rate": overall_win_rate,
            "trending": "up" if recent_win_rate > overall_win_rate else "down" if recent_win_rate < overall_win_rate else "stable"
        }
    
    def list_all_athletes(self) -> List[Dict]:
        """Get list of all accessible athletes based on user role."""
        athletes = []
        seen_athlete_ids = set()
        
        for athlete_dir in self._get_athlete_dirs():
            if not os.path.exists(athlete_dir):
                continue
                
            for filename in os.listdir(athlete_dir):
                if filename.endswith('.json'):
                    athlete_id = filename[:-5]  # Remove .json
                    
                    # Avoid duplicates
                    if athlete_id in seen_athlete_ids:
                        continue
                    
                    try:
                        profile_path = os.path.join(athlete_dir, filename)
                        with open(profile_path, 'r') as f:
                            profile = json.load(f)
                        
                        # Check access permissions
                        if self._can_access_athlete(profile):
                            athletes.append(profile)
                            seen_athlete_ids.add(athlete_id)
                    except (json.JSONDecodeError, IOError):
                        continue  # Skip corrupted files
        
        return sorted(athletes, key=lambda x: x.get("name", ""))
    
    def search_athletes(self, query: str) -> List[Dict]:
        """Search athletes by name or team."""
        all_athletes = self.list_all_athletes()
        query_lower = query.lower()
        
        matches = []
        for athlete in all_athletes:
            if (query_lower in athlete.get("name", "").lower() or 
                query_lower in athlete.get("team", "").lower()):
                matches.append(athlete)
        
        return matches
    
    def get_team_analysis(self, team_name: str) -> Dict:
        """Analyze performance across all accessible athletes from a team."""
        all_athletes = self.list_all_athletes()
        team_athletes = [a for a in all_athletes 
                        if team_name.lower() in a.get("team", "").lower()]
        
        if not team_athletes:
            return {"error": f"No accessible athletes found for team: {team_name}"}
        
        team_stats = {
            "team_name": team_name,
            "total_athletes": len(team_athletes),
            "total_matches": 0,
            "overall_win_rate": 0,
            "top_performers": [],
            "improvement_champions": []
        }
        
        all_win_rates = []
        all_improvements = []
        
        for athlete in team_athletes:
            athlete_analysis = self.get_progress_analysis(athlete["athlete_id"])
            if "error" not in athlete_analysis:
                matches = athlete_analysis.get("win_loss_record", {}).get("total_matches", 0)
                team_stats["total_matches"] += matches
                
                win_rate = athlete_analysis.get("win_loss_record", {}).get("win_percentage", 0)
                if matches > 0:  # Only include athletes with matches
                    all_win_rates.append(win_rate)
                
                # Calculate overall improvement
                trends = athlete_analysis.get("assessment_trends", {})
                total_improvement = sum(data.get("improvement", 0) for data in trends.values())
                all_improvements.append({
                    "name": athlete["name"],
                    "improvement": total_improvement,
                    "win_rate": win_rate,
                    "matches": matches
                })
        
        if all_win_rates:
            team_stats["overall_win_rate"] = round(statistics.mean(all_win_rates), 1)
        
        # Filter to only include athletes with matches
        athletes_with_matches = [a for a in all_improvements if a["matches"] > 0]
        
        # Top performers (by win rate)
        team_stats["top_performers"] = sorted(
            athletes_with_matches, key=lambda x: x["win_rate"], reverse=True
        )[:5]
        
        # Most improved (by total improvement score)
        team_stats["improvement_champions"] = sorted(
            athletes_with_matches, key=lambda x: x["improvement"], reverse=True
        )[:5]
        
        return team_stats

    def list_all_reviews(self) -> List[Dict]:
        """Get list of all accessible reviews for editing based on user role."""
        reviews = []
        seen_review_ids = set()
        
        for review_dir in self._get_review_dirs():
            if not os.path.exists(review_dir):
                continue
                
            for filename in os.listdir(review_dir):
                if filename.endswith('.json'):
                    review_id = filename[:-5]  # Remove .json
                    
                    # Avoid duplicates
                    if review_id in seen_review_ids:
                        continue
                    
                    try:
                        review_path = os.path.join(review_dir, filename)
                        with open(review_path, 'r') as f:
                            review_data = json.load(f)
                        
                        # Check ownership for security (except admin)
                        if self.user_role != "admin":
                            review_owner = review_data.get("metadata", {}).get("owner")
                            
                            # If this is from global directory and user is not admin,
                            # only include reviews owned by current user
                            if review_dir.endswith(os.path.join(self.base_dir, "reviews")):
                                if review_owner != self.current_user:
                                    continue  # Skip reviews not owned by current user
                        
                        # Extract key info for display
                        match_info = review_data.get("match_info", {})
                        metadata = review_data.get("metadata", {})
                        
                        review_summary = {
                            "review_id": review_id,
                            "fighter_a": match_info.get("fighter_a", "Unknown"),
                            "fighter_b": match_info.get("fighter_b", "Unknown") or "Unknown Opponent",
                            "match_description": match_info.get("match_number", ""),
                            "event": match_info.get("event", ""),
                            "date": metadata.get("reviewed_at", "")[:10],
                            "result": match_info.get("result", ""),
                            "total_events": len(review_data.get("timeline", [])),
                            "review_path": review_path
                        }
                        
                        reviews.append(review_summary)
                        seen_review_ids.add(review_id)
                        
                    except (json.JSONDecodeError, IOError):
                        continue  # Skip corrupted files
        
        # Sort by date (newest first) then by review_id
        reviews.sort(key=lambda x: (x.get("date", ""), x.get("review_id", "")), reverse=True)
        return reviews

    def load_review_for_editing(self, review_id: str) -> Optional[Dict]:
        """Load a complete review for editing in the app."""
        for review_dir in self._get_review_dirs():
            review_path = os.path.join(review_dir, f"{review_id}.json")
            if os.path.exists(review_path):
                try:
                    with open(review_path, 'r') as f:
                        return json.load(f)
                except (json.JSONDecodeError, IOError):
                    continue
        return None
    
    def save_review_to_user_directory(self, review_id: str, review_data: Dict) -> str:
        """Save a review to the current user's directory."""
        review_dir = self._get_user_review_dir()
        review_path = os.path.join(review_dir, f"{review_id}.json")
        
        # Add owner information to review
        review_data["owner"] = self.current_user
        review_data.setdefault("metadata", {})["owner"] = self.current_user
        
        with open(review_path, 'w') as f:
            json.dump(review_data, f, indent=2)
        
        return review_path
    
    def get_accessible_teams(self) -> List[str]:
        """Get list of team names the current user can access."""
        athletes = self.list_all_athletes()
        teams = set()
        
        for athlete in athletes:
            team = athlete.get("team", "").strip()
            if team:
                teams.add(team)
        
        return sorted(list(teams))
    
    def get_user_statistics(self) -> Dict:
        """Get statistics for the current user."""
        athletes = self.list_all_athletes()
        
        stats = {
            "total_athletes": len(athletes),
        missing_athlete_id_files = []
        for athlete_dir in self._get_athlete_dirs():
            if not os.path.exists(athlete_dir):
                continue
            for filename in os.listdir(athlete_dir):
                if filename.endswith('.json'):
                    try:
                        profile_path = os.path.join(athlete_dir, filename)
                        with open(profile_path, 'r') as f:
                            profile = json.load(f)
                        # Skip and warn if missing 'athlete_id'
                        if 'athlete_id' not in profile:
                            missing_athlete_id_files.append(profile_path)
                            continue
                        athlete_id = profile['athlete_id']
                        # Avoid duplicates
                        if athlete_id in seen_athlete_ids:
                            continue
                        # Check access permissions
                        if self._can_access_athlete(profile):
                            athletes.append(profile)
                            seen_athlete_ids.add(athlete_id)
                    except (json.JSONDecodeError, IOError):
                        continue  # Skip corrupted files
        if missing_athlete_id_files:
            import streamlit as st
            st.warning(f"{len(missing_athlete_id_files)} athlete file(s) missing 'athlete_id' and were skipped: {missing_athlete_id_files}")
        return sorted(athletes, key=lambda x: x.get("name", ""))
            key=lambda x: x["date"], reverse=True
        )
        stats["recent_activity"] = stats["recent_activity"][:10]  # Keep only 10 most recent
        
        return stats
    
    def delete_match_review(self, athlete_id: str, review_id: str) -> bool:
        """Delete a match review and unlink it from athlete."""
        try:
            success = False
            
            # Remove from athlete's match history
            profile = self.get_athlete_profile(athlete_id)
            if profile and review_id in profile.get("match_history", []):
                profile["match_history"].remove(review_id)
                
                # Find and update the athlete profile file
                for athlete_dir in self._get_athlete_dirs():
                    profile_path = os.path.join(athlete_dir, f"{athlete_id}.json")
                    if os.path.exists(profile_path):
                        with open(profile_path, 'w') as f:
                            json.dump(profile, f, indent=2)
                        break
                
                success = True
            
            # Delete the review file from accessible directories
            for review_dir in self._get_review_dirs():
                review_path = os.path.join(review_dir, f"{review_id}.json")
                if os.path.exists(review_path):
                    os.remove(review_path)
                    success = True
                    break
            
            return success
            
        except Exception as e:
            print(f"Error deleting match review {review_id}: {e}")
            return False
    
    def update_match_review(self, review_id: str, updated_review_data: Dict) -> bool:
        """Update an existing match review."""
        try:
            # Find and update the review file
            for review_dir in self._get_review_dirs():
                review_path = os.path.join(review_dir, f"{review_id}.json")
                if os.path.exists(review_path):
                    # Add update metadata
                    updated_review_data.setdefault("metadata", {})
                    updated_review_data["metadata"]["last_updated"] = datetime.now().isoformat()
                    
                    with open(review_path, 'w') as f:
                        json.dump(updated_review_data, f, indent=2)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error updating match review {review_id}: {e}")
            return False