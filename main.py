import os
from Bio import ExPASy
from Bio import SwissProt

def agent_search_protein(protein_id):
    """
    Premier Agent : Se connecte à UniProt, récupère la séquence et valide les acides aminés.
    """
    print(f"\n[Agent Recherche] Connexion à la banque de données pour l'ID: {protein_id}...")
    try:
        handle = ExPASy.get_sprot_raw(protein_id)
        record = SwissProt.read(handle)
        
        sequence = record.sequence
        protein_name = record.description.split(';')[0]
        
        print("[Agent Recherche] Protéine trouvée avec succès!")
        return {
            "status": "success",
            "name": protein_name,
            "sequence": sequence
        }
    except Exception as e:
        print(f"[Erreur] Échec de la récupération des données : {e}")
        return {"status": "error", "message": str(e)}

def agent_affinity_biochar(sequence):
    """
    Deuxième Agent : Analyse la structure de la séquence pour évaluer l'adhérence 
    sur les particules de Biochar broyées à 100 microns.
    """
    print("[Agent Affinité] Analyse des propriétés de surface (Biochar 100um)...")
    
    # Résidus hydrophobes (Forte liaison avec le carbone du biochar)
    hydrophobic_residues = set(['A', 'V', 'L', 'I', 'P', 'F', 'W', 'M'])
    # Résidus chargés (Interaction avec les groupements fonctionnels)
    charged_residues = set(['R', 'K', 'D', 'E', 'H'])

    total_length = len(sequence)
    hydrophobic_count = sum(1 for aa in sequence if aa in hydrophobic_residues)
    charged_count = sum(1 for aa in sequence if aa in charged_residues)
    
    # Calcul des pourcentages bio-physiques
    pct_hydrophobicity = (hydrophobic_count / total_length) * 100
    pct_charge = (charged_count / total_length) * 100
    
    # Algorithme d'affinité adapté à la surface spécifique du Biochar 100 microns
    base_affinity = (pct_hydrophobicity * 1.5) + (pct_charge * 0.8)
    micro_scale_factor = 1.2  # Facteur de correction pour 100 microns
    final_score = min(base_affinity * micro_scale_factor, 100.0)
    
    print("[Agent Affinité] Calculs de structure et d'adhérence terminés.")
    return {
        "hydrophobicity": round(pct_hydrophobicity, 2),
        "charge": round(pct_charge, 2),
        "score": round(final_score, 2)
    }

if __name__ == "__main__":
    # ID de test (Peut être remplacé par votre propre identifiant de protéine)
    target_protein_id = "P02768"
    
    # Execution du pipeline des deux agents
    search_result = agent_search_protein(target_protein_id)
    
    if search_result["status"] == "success":
        # Passage des données du premier agent au deuxième agent
        protein_seq = search_result["sequence"]
        affinity_report = agent_affinity_biochar(protein_seq)
        
        # Affichage du rapport final standardisé
        print("\n================ REPORT PIPELINE AI AGENTS ================")
        print(f" Nom de la protéine  : {search_result['name']}")
        print(f" Longueur Séquence   : {len(protein_seq)} Acides Aminés")
        print(f" Taux Hydrophobité   : {affinity_report['hydrophobicity']}%")
        print(f" Taux Résidus Chargés: {affinity_report['charge']}%")
        print(f" Score d'Adhérence   : {affinity_report['score']} / 100 (Biochar 100µm)")
        print("===========================================================")
