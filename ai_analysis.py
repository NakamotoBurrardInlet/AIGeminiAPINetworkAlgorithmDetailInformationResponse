# ai_analysis.py

from google import genai
from google.genai import types
import json

# --- Acceptable "AI Algorithm to Speed Up" ---
# This algorithm speeds up performance by providing actionable insights, 
# not by manipulating packets.

def analyze_and_suggest(api_key: str, data_history: list):
    """
    Analyzes historical network performance data using the Gemini API 
    and suggests non-invasive optimizations.
    """
    if not api_key:
        return "AI Analysis: Please enter your Gemini API Key."

    try:
        client = genai.Client(api_key=api_key)
        
        # Format the data history for the AI model
        analysis_data = json.dumps(data_history[-50:]) # Send last 50 data points
        
        prompt = (
            "Analyze this JSON list of network performance logs (latency, bytes sent/recv, system load). "
            "Identify potential non-network bottlenecks (e.g., high CPU/RAM usage during high traffic). "
            "Provide one actionable, non-intrusive suggestion to improve speed or stability. "
            "Suggestions must focus on system configuration, like 'Close Process X' or 'Update DNS settings'."
            f"Data: {analysis_data}"
        )
        
        # Use a high-performance model for quick analysis
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        return response.text
        
    except types.BlockedPromptError:
        return "AI Analysis Blocked: Query contained sensitive or policy-violating content."
    except Exception as e:
        return f"AI Analysis Error: {e}"
