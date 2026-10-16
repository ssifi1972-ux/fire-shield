import streamlit as st
import numpy as np
import pandas as pd
from Bio import ExPASy
from Bio import SwissProt

st.set_page_config(page_title="Fire-Shield Biochar AI", page_icon="🌱", layout="centered")

def agent_search_protein(protein_id):
    """ Premier Agent : Recherche et validation de la séquence """
    try:
        handle = ExPASy.get_sprot_raw(protein_id)
        record = SwissProt.read(handle)
        return {"status": "success", "name": record.description.split(';')[0], "sequence": record.sequence}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def agent_affinity_biochar(sequence):
    """ Deuxième Agent : Analyse de l'adhérence sur Biochar 100µm """
    hydrophobic_residues = set(['A', 'V', 'L', 'I', 'P', 'F', 'W', 'M'])
    charged_residues = set(['R', 'K', 'D', 'E', 'H'])
    
    total_length = len(sequence)
    hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic_residues)
    charged_count = sum(1 for aa in sequence if aa in charged_residues)
    
    pct_hydrophobicity = (hydrophobic_count / total_length) * 100
    pct_charge = (charged_count / total_length) * 100
    
    base_affinity = (pct_hydrophobicity * 1.5) + (pct_charge * 0.8)
    final_score = min(base_affinity * 1.2, 100.0)
    
    return {"hydrophobicity": round(pct_hydrophobicity, 2), "charge": round(pct_charge, 2), "score": round(final_score, 2)}

# --- INTERFACE UTILISATEUR (UI) ---
st.title("🌱 Fire-Shield AI : Bio-Intelligence System")
st.markdown("### Analyse d'adhérence des protéines sur particules de Biochar (100 microns)")

protein_input = st.text_input("Entrez l'identifiant de la protéine (ex: P02768):", "P02768")

if st.button("Lancer l'Analyse Spécifique"):
    with st.spinner("Les agents IA analysent la structure..."):
        search_result = agent_search_protein(protein_input)
        
        if search_result["status"] == "success":
            seq = search_result["sequence"]
            report = agent_affinity_biochar(seq)
            
            st.success("Analyse terminée avec succès par les agents !")
            
            # Affichage des métriques principales
            st.subheader(f"Rapport : {search_result['name']}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Score d'Adhérence", f"{report['score']} / 100")
            col2.metric("Hydrophobité", f"{report['hydrophobicity']}%")
            col3.metric("Résidus Chargés", f"{report['charge']}%")
            
            # --- AJOUT DU GRAPHIQUE ---
            st.write("#### Visualisation des propriétés de surface :")
            chart_data = pd.DataFrame({
                'Propriétés': ['Hydrophobité (Liaison Carbone)', 'Résidus Chargés'],
                'Pourcentage (%)': [report['hydrophobicity'], report['charge']]
            })
            st.bar_chart(data=chart_data, x='Propriétés', y='Pourcentage (%)', use_container_width=True)
            
            with st.expander("Voir la séquence d'acides aminés validée"):
                st.code(seq, language="text")
        else:
            st.error(f"Erreur de l'agent : {search_result['message']}")
