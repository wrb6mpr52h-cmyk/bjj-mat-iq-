from supabase import create_client, Client

SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"  # Replace with your Supabase URL
SUPABASE_KEY = "YOUR_SUPABASE_API_KEY"  # Replace with your Supabase API key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_athlete_supabase(coach_id, name, belt, weight_class, notes):
    data = {
        "coach_id": coach_id,
        "name": name,
        "belt": belt,
        "weight_class": weight_class,
        "notes": notes
    }
    result = supabase.table("athletes").insert(data).execute()
    return result

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
