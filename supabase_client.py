import os
from dotenv import load_dotenv
load_dotenv()
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_supabase_connection():
    """Test the Supabase connection by listing tables or fetching a simple response."""
    try:
        # Try to fetch a list of tables (or a simple select from a known table)
        response = supabase.table("athletes").select("*").limit(1).execute()
        print("Supabase connection successful! Response:", response)
        return True
    except Exception as e:
        print("Supabase connection failed:", e)
        return False

def create_athlete_supabase(coach_id, name, belt, weight_class, notes):
    data = {
        "coach_id": coach_id,
        "name": name,
        "belt": belt,
        "weight_class": weight_class,
        "notes": notes
    }
    try:
        result = supabase.table("athletes").insert(data).execute()
        return result
    except Exception as e:
        print("Supabase insert error:", e)
        print("Data sent:", data)
        raise

def create_match_supabase(athlete_id, coach_id, event_name, video_url):
    data = {
        "athlete_id": athlete_id,
        "coach_id": coach_id,
        "event_name": event_name,
        "video_url": video_url
    }
    result = supabase.table("matches").insert(data).execute()
    return result

def create_review_supabase(match_id, coach_id, review_json, timeline, heatmap, key_moments, strengths, fixes, drills):
    data = {
        "match_id": match_id,
        "coach_id": coach_id,
        "review_json": review_json,
        "timeline": timeline,
        "heatmap": heatmap,
        "key_moments": key_moments,
        "strengths": strengths,
        "fixes": fixes,
        "drills": drills
    }
    result = supabase.table("reviews").insert(data).execute()
    return result
