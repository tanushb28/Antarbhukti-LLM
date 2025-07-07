
#!/usr/bin/env python3
# """
# Driver script for Petri Net containment checking.
# This script demonstrates how to use the Verifier and GenReport classes
# to perform containment analysis and generate reports.
# """

from src.antarbhukti.sfc import SFC
from src.antarbhukti.sfc_verifier import Verifier
from src.antarbhukti.genreport import GenReport
from src.antarbhukti.llm_manager import LLM_Mgr

def check_pn_containment_html(verifier, gen_report, sfc1, pn1, sfc2, pn2):
    gen_report.sfc_to_dot(sfc1, "sfc1.dot")
    gen_report.dot_to_png("sfc1.dot", "sfc1.png")
    gen_report.petrinet_to_dot(pn1, "pn1.dot")
    gen_report.dot_to_png("pn1.dot", "pn1.png")
    gen_report.sfc_to_dot(sfc2, "sfc2.dot")
    gen_report.dot_to_png("sfc2.dot", "sfc2.png")
    gen_report.petrinet_to_dot(pn2, "pn2.dot")
    gen_report.dot_to_png("pn2.dot", "pn2.png")

     # Prepare image paths for report

    img_paths = {
        "sfc1": gen_report.img_to_base64("sfc1.png"),
        "pn1": gen_report.img_to_base64("pn1.png"),
        "sfc2": gen_report.img_to_base64("sfc2.png"),
        "pn2": gen_report.img_to_base64("pn2.png")
    }

     # Use GenReport instance to generate HTML report

    return gen_report.generate_containment_html_report(
        verifier.cutpoints1, verifier.cutpoints2, verifier.paths1, verifier.paths2, 
        verifier.matches1, verifier.unmatched1, verifier.contained, img_paths
    )

def main():
    """Main driver function for Petri Net containment analysis."""
    # Create verifier and report generator instances
    verifier = Verifier()
    gen_report = GenReport()
    llm_mng = LLM_Mgr()
    
    # Load SFC models
    
    sfc1 = SFC()
    sfc2 = SFC()
    sfc1.load("data/dec2hex.txt")
    sfc2.load("data/dec2hex_mod.txt")

    # Iteration count for iterative prompting 

    for iter_count in range(10):
        print(f"\n--- Containment Iteration {iter_count + 1} ---")
        # Convert SFC models to Petri nets

        pn1 = verifier.sfc_to_petrinet(sfc1)
        pn2 = verifier.sfc_to_petrinet(sfc2)

        # Perform containment analysis

        verifier.check_pn_containment(sfc1, pn1, sfc2, pn2)

        # Generate HTML report

        html_report = check_pn_containment_html(verifier, gen_report, sfc1, pn1, sfc2, pn2)
        
        # Write report to file

        with open("pn_containment_report.html", "w") as f:
            f.write(html_report)
        print("HTML report written to pn_containment_report.html")

        # Demonstrate access to analysis results

        print(f"Model 1 contained in Model 2: {verifier.is_contained()}")
        print(f"Number of unmatched paths: {len(verifier.get_unmatched_paths())}")
        print(f"Number of matched paths: {len(verifier.get_matched_paths())}")
        if verifier.is_contained():
            print("Containment achieved.")
            break
        
        # Call LLM to improve SFC2 if needed
        
        improved = llm_mng.improve_sfc2(
            sfc1, sfc2, verifier.get_unmatched_paths(),
            prompt_path=f"prompt_refiner_iter{iter_count+1}.txt",
            sfc2_path="dec2hex_mod.txt"
        )
        if not improved:
            print("No further improvement possible or LLM failed.")
            break
        sfc2 = SFC()
        sfc2.load("data/dec2hex_mod.txt")

if __name__ == "__main__":
    main()
