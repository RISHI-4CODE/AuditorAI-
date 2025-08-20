import requests, streamlit as st

st.set_page_config(page_title="AuditorAgent Dashboard", layout="wide")
st.title("AuditorAgent – Recent Audits")

url = st.text_input("Logs API URL", "http://localhost:8000/logs")
if st.button("Refresh") or True:
    try:
        data = requests.get(url, timeout=5).json().get("items", [])
    except Exception as e:
        st.error(f"Failed: {e}")
        st.stop()

    for item in data:
        with st.container(border=True):
            st.write(f"**Status:** {item.get('status')} | **At:** {item.get('ts','')}")
            st.write("**Input:**", item.get("input",""))
            res = item.get("result",{})
            st.write(f"**Risk:** {res.get('risk_score')} | Issues: {', '.join(res.get('issues',[]))}")
            if res.get("pii"):
                st.write("**PII:**", res["pii"])
            if res.get("safe_output"):
                st.write("**Safe Output:**")
                st.code(res["safe_output"])
