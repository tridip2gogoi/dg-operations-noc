                    h1, h2, h3 = st.columns(3)
                    h1.metric("Previous Docket No (Col AA)", str(site_row.get('Previous Docket No.', 'None')))
                    h2.metric("Previous Raise Date (Col AB)", clean_date_str(site_row.get('Previous Docket raise Date', 'None')))
                    h3.metric("Last Closed Date", last_closed_val if last_closed_val else 'None')

                    st.markdown("<hr style='margin: 10px 0; border-color: #facc15;'>", unsafe_allow_html=True)
                    st.markdown(f"**Previous Resolution Remarks (Col Z):**")
                    prev_rem_text = str(site_row.get('Previous Remarks', 'No previous historical remarks recorded.'))
                    st.markdown(f"""
                    <div class="previous-remarks-box">
                        {prev_rem_text}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- COL AC (FSR PDF LINK) FULL INTEGRATION WITH CLICKABLE LINK OR BUTTON ---
                    pdf_link_val = str(site_row.get('Col AC (FSR PDF link)', site_row.get('FSR PDF Link', 'None'))).strip()
                    if pdf_link_val and pdf_link_val.lower() not in ['', 'nan', 'none', '0', '0.0']:
                        st.markdown(f"""
                        <div style="margin-top: 10px; background-color: rgba(30, 41, 59, 0.9); border: 1px solid #38bdf8; padding: 12px; border-radius: 6px;">
                            <b style="color: #38bdf8;">📄 Col AC (FSR PDF Link / Record):</b><br>
                            <span style="color: #ffffff; font-size: 13px;">{pdf_link_val}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Check if it's a URL (Google Drive or http/https)
                        if pdf_link_val.startswith(('http://', 'https://', 'www.')):
                            target_url = pdf_link_val if pdf_link_val.startswith('http') else f"https://{pdf_link_val}"
                            st.link_button("🌐 Open FSR PDF / Google Drive Link", target_url, use_control_width=True if hasattr(st, "link_button") else False)
                        else:
                            # Render a clickable anchor tag if it contains text or link reference
                            st.markdown(f"""
                            <div style="margin-top: 6px;">
                                <a href="{pdf_link_val}" target="_blank" style="color: #38bdf8; font-weight: bold; text-decoration: underline;">🔗 Click here to Open FSR Document / Link</a>
                            </div>
                            """, unsafe_allow_html=True)
