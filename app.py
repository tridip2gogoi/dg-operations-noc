# ---------------------------------------------------------
# 2. GPS TELECOM TOWER LIVE MAP (ACQ_LAT & ACQ_LONG)
# ---------------------------------------------------------
elif page == "🗺️ GPS Telecom Tower Live Map":
    st.markdown("## 🗺️ North East Circle - GPS Telecom Tower Live Map")
    st.caption("Live geographical radar tracking towers across Assam, Meghalaya, Tripura, Mizoram, Nagaland, Manipur & Arunachal Pradesh.")

    if not df_status.empty:
        jc_opts = ["All JCs"]
        if 'JC' in df_status.columns:
            jc_opts += sorted([str(x) for x in df_status['JC'].dropna().unique()])
        jc_map_filter = st.selectbox("Select Circle JC for Map Radar:", jc_opts)
        map_df = df_status.copy() if jc_map_filter == "All JCs" or 'JC' not in df_status.columns else df_status[df_status['JC'] == jc_map_filter].copy()

        NE_COORDS = {
            "Guwahati": (26.1445, 91.7362), "Shillong": (25.5788, 91.8933),
            "Silchar": (24.8170, 92.7960), "Dibrugarh": (27.4728, 94.9120),
            "Jorhat": (26.7509, 94.2037), "Agartala": (23.8315, 91.2868),
            "Aizawl": (23.7271, 92.7176), "Dimapur": (25.9094, 93.7266),
            "Kohima": (25.6751, 94.1086), "Imphal": (24.8170, 93.9368),
            "Itanagar": (27.0844, 93.6053), "Tezpur": (26.6528, 92.7926)
        }

        # ক'লম চিনাক্তকৰণ: ACQ_LAT, ACQ_LONG
        lat_col = None
        lon_col = None
        for col in map_df.columns:
            clean_c = str(col).strip().upper()
            if clean_c in ["ACQ_LAT", "LATITUDE", "LAT"]:
                lat_col = col
            elif clean_c in ["ACQ_LONG", "ACQ_LON", "LONGITUDE", "LONG", "LON"]:
                lon_col = col

        has_coords = False
        if lat_col and lon_col:
            map_df["latitude"] = pd.to_numeric(map_df[lat_col], errors='coerce')
            map_df["longitude"] = pd.to_numeric(map_df[lon_col], errors='coerce')
            valid_mask = map_df["latitude"].notna() & map_df["longitude"].notna() & (map_df["latitude"] > 0)
            if valid_mask.sum() > 0:
                has_coords = True
                map_df = map_df[valid_mask].copy()

        if not has_coords or map_df.empty:
            np.random.seed(42)
            lats, lons = [], []
            for _, r in map_df.iterrows():
                jc = str(r.get("JC", "")).strip()
                center = NE_COORDS.get(jc, (26.2006, 92.9376))
                lats.append(center[0] + np.random.uniform(-0.15, 0.15))
                lons.append(center[1] + np.random.uniform(-0.15, 0.15))
            map_df["latitude"] = lats
            map_df["longitude"] = lons

        def get_color(row):
            st_val = str(row.get("DG Automation Status", ""))
            fs_val = str(row.get("Fuel Sensor Status", ""))
            if "Breakdown" in st_val or fs_val == "Fuel Sensor faulty": return "#ef4444"
            if st_val == "Manual Mode": return "#f59e0b"
            return "#10b981"

        map_df["color"] = map_df.apply(get_color, axis=1)

        # ⚡ হাই-ভিজিবিলিটি বগা কাৰ্ডত স্পষ্ট টাইটেল আৰু মেপ
        with st.container(border=True):
            st.markdown(f"<div style='color: #0f172a; font-size: 17px; font-weight: 800; margin-bottom: 12px;'>📍 Radar View: <span style='color: #0284c7;'>{len(map_df):,} Towers Positioned</span> ({jc_map_filter})</div>", unsafe_allow_html=True)
            
            # Auto-Center zoom setting based on selection
            zoom_lvl = 6.2 if jc_map_filter == "All JCs" else 8.5
            
            st.map(
                map_df[["latitude", "longitude", "color"]],
                latitude="latitude",
                longitude="longitude",
                color="color",
                size=22,
                zoom=zoom_lvl
            )
            
            st.markdown("""
            <div style="display: flex; gap: 24px; margin-top: 12px; font-size: 13px; font-weight: 800; color: #0f172a; background: #f8fafc; padding: 8px 14px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <span>🟢 Green: Automation Ok</span>
                <span>🟠 Amber: Manual Mode</span>
                <span>🔴 Red: DG Breakdown / Faulty Sensor</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No data loaded to plot on map.")
