from supabase import create_client, Client

SUPABASE_URL = "https://gfcvphrbgmmrwtwdwdwt.supabase.co"  # Replace with your Supabase URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdmY3ZwaHJiZ21tcnd0d2R3ZHd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcxNjc1MzAsImV4cCI6MjA5Mjc0MzUzMH0.anRLaqI6wmW-sSN5BcStOJgdRyqvAKLm03A1qo1Cw4s"
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
