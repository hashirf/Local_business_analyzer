import streamlit as st
import requests
import pandas as pd
import re


def search_places(api_key, query, zip_code):
    radius = 2500 
    endpoint = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    results = []
    max_radius = 50000  

    while radius <= max_radius:
        params = {
            'query': f"{query} near {zip_code}",
            'key': api_key,
            'radius': radius
        }
        response = requests.get(endpoint, params=params)
        new_results = response.json().get('results', [])
        
  
        results.extend(new_results)
        unique_results = list({place['place_id']: place for place in results}.values())
        
    
        if len(unique_results) >= 10:
            results = unique_results
            break 
        radius += 2500
    return results

def get_directions(api_key, origin, destination):
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json'
    params = {'origin': origin, 'destination': destination, 'key': api_key}
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        directions = response.json()
        for route in directions.get('routes', []):
            for leg in route.get('legs', []):
                return leg.get('distance', {}).get('text', ''), leg.get('duration', {}).get('text', '')
    return "", ""


def extract_zip_code_from_address(address):
    match = re.search(r'\b\d{5}\b', address)
    return match.group(0) if match else None


def main():
    st.title("ZIP Code Specific Places Finder and Distance Calculator")
    
    api_key = st.text_input("Enter your Google Maps API Key:", type="password")
    
    zip_code = st.text_input("📍 ZIP Code for Places Search:")
    search_terms_input = st.text_input("Search Terms (e.g., 'hvac repair, plumbing'):", help="Enter search terms separated by commas.")
    target_location = st.text_input("Target Location for Distance Calculation:")

    if st.button("Search Places and Calculate Distances"):
        if not api_key or not zip_code or not search_terms_input or not target_location:
            st.error("Please fill in all fields.")
        else:
            all_results = []
            search_terms = [term.strip() for term in search_terms_input.split(',')]
            
            for search_term in search_terms:
                places = search_places(api_key, search_term, zip_code)
                if places:
                    for place in places:
                        place_name = place["name"]
                        place_address = place.get("formatted_address", "Address not available")
                        distance, duration = get_directions(api_key, place_address, target_location)
                        zip_code_extracted = extract_zip_code_from_address(place_address)
                        result = {
                            "Search Term": search_term,
                            "Name": place_name,
                            "Address": place_address,
                            "ZIP Code": zip_code_extracted,
                            "Distance": distance,
                            "Duration": duration
                        }
                        all_results.append(result)
            
            if all_results:
                df_results = pd.DataFrame(all_results)
                st.write(df_results)
               
                csv = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name='places_distances.csv',
                    mime='text/csv',
                )
            else:
                st.write("No places found for the given search terms in the ZIP code area.")

if __name__ == "__main__":
    main()




